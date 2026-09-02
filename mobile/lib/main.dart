import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AzClceApp());
}

const String limitation =
    'CLCE detects inconsistency, not intent. Type D is a label, not a '
    'finding of malice. Human validation required. Not a cybersecurity '
    'exploit, not a scanner of other people\'s systems, not a lie detector. '
    'Advisory scores only. Threshold 0.7 is the paper\'s acceptable line, '
    'not a pass/fail of truth.';

const double kThreshold = 0.7;
const double kVeryLow = 0.3;
const double kHighN = 0.5;

const Map<String, String> kidPlainBand = {
  'perfect':
      'These three stories match. What it looks like, what they wrote, and what it actually does use the same words.',
  'acceptable':
      'These stories are close enough. A grown-up should still check, because close is not the same as perfect.',
  'structural inconsistency':
      'These stories do not match. The picture, the writing, and the real thing are talking about different stuff.',
};

const Map<String, String> kidPlainTypes = {
  'A': 'The picture and the writing do not match, but the real thing is closer to one of them.',
  'B': 'The picture and the writing match, but the real thing is different.',
  'C': 'Important pieces are missing, or none of the three stories really agree.',
  'D':
      'LABEL ONLY. The picture matches the writing, but the real thing is very different and lots of pieces are missing. This does not mean anyone was trying to trick you. CLCE finds mismatches, not motives.',
};

Set<String> tokenize(String text) {
  final lower = text.toLowerCase();
  final out = <String>{};
  final buf = StringBuffer();
  void flush() {
    if (buf.isNotEmpty) {
      out.add(buf.toString());
      buf.clear();
    }
  }

  for (final r in lower.runes) {
    final ok = (r >= 97 && r <= 122) || (r >= 48 && r <= 57);
    if (ok) {
      buf.writeCharCode(r);
    } else {
      flush();
    }
  }
  flush();
  return out;
}

double jaccard(Set<String> a, Set<String> b, [Set<String>? c]) {
  final groups = c == null ? [a, b] : [a, b, c];
  if (groups.every((s) => s.isEmpty)) return 1.0;
  final union = <String>{};
  for (final s in groups) {
    union.addAll(s);
  }
  if (union.isEmpty) return 1.0;
  var inter = Set<String>.from(groups.first);
  for (final s in groups.skip(1)) {
    inter = inter.intersection(s);
  }
  return inter.length / union.length;
}

class Report {
  Report({
    required this.triple,
    required this.rd,
    required this.dp,
    required this.rp,
    required this.avg,
    required this.plus,
    required this.band,
    required this.types,
    required this.primary,
    required this.kidPlain,
  });

  final double triple;
  final double rd;
  final double dp;
  final double rp;
  final double avg;
  final double plus;
  final String band;
  final List<String> types;
  final String? primary;
  final String kidPlain;
}

const typeLabels = {
  'A': 'Surface Error',
  'B': 'Functional Error',
  'C': 'Structural Gap',
  'D': 'Intentional Obfuscation (label only)',
};

const typeNotes = {
  'A': 'R↔D is low while D↔P and R↔P are higher: docs/UI disagree; function is closer to one layer.',
  'B': 'R↔D is high while D↔P or R↔P is low: pretty alignment, function diverges.',
  'C': 'High |N| relative to the union, or all pairwise mediocre and the triple score is below 0.7.',
  'D': 'LABEL ONLY. High N and D↔P very low and R↔D high. CLCE detects inconsistency, not intent. Not a finding of malice.',
};

Report scoreLayers(String r, String d, String p, String n) {
  final tr = tokenize(r);
  final td = tokenize(d);
  final tp = tokenize(p);
  final tn = tokenize(n);
  final union = {...tr, ...td, ...tp};
  final inter = tr.intersection(td).intersection(tp);
  final triple = jaccard(tr, td, tp);
  final rd = jaccard(tr, td);
  final dp = jaccard(td, tp);
  final rp = jaccard(tr, tp);
  final avg = (rd + dp + rp) / 3.0;
  final denom = union.length + tn.length;
  final plus = denom == 0 ? 1.0 : inter.length / denom;
  final nRatio = tn.length / (union.isEmpty ? 1 : union.length);
  final highN = nRatio >= kHighN;
  final types = <String>[];
  if (highN && dp < kVeryLow && rd >= kThreshold) types.add('D');
  final allMediocre = rd < kThreshold && dp < kThreshold && rp < kThreshold;
  if (highN || (allMediocre && triple < kThreshold)) types.add('C');
  if (rd >= kThreshold && (dp < kThreshold || rp < kThreshold)) types.add('B');
  if (rd < kThreshold && dp > rd && rp > rd) types.add('A');
  String band;
  if (triple >= 1.0 - 1e-12) {
    band = 'perfect';
  } else if (triple >= kThreshold) {
    band = 'acceptable';
  } else {
    band = 'structural inconsistency';
  }
  final parts = <String>[
    kidPlainBand[band] ?? kidPlainBand['structural inconsistency']!,
  ];
  if (types.isEmpty) {
    parts.add('No mismatch type matched. A grown-up should still check.');
  } else {
    for (final code in types) {
      final note = kidPlainTypes[code];
      if (note != null) parts.add('Type $code: $note');
    }
  }
  parts.add('CLCE detects inconsistency, not intent. Type D is a label only.');
  return Report(
    triple: triple,
    rd: rd,
    dp: dp,
    rp: rp,
    avg: avg,
    plus: plus,
    band: band,
    types: types,
    primary: types.isEmpty ? null : types.first,
    kidPlain: parts.join(' '),
  );
}

Map<String, String> parseLayersText(String raw) {
  final blob = raw.trim();
  if (blob.isEmpty) {
    return {'r': '', 'd': '', 'p': '', 'n': ''};
  }
  if (blob.startsWith('{')) {
    final obj = jsonDecode(blob);
    if (obj is Map) {
      String pick(List<String> keys) {
        for (final k in keys) {
          if (obj[k] != null) return obj[k].toString();
        }
        return '';
      }

      return {
        'r': pick(['r', 'R', 'representation']),
        'd': pick(['d', 'D', 'description']),
        'p': pick(['p', 'P', 'reality']),
        'n': pick(['n', 'N', 'negative', 'missing']),
      };
    }
  }
  final buckets = {'r': <String>[], 'd': <String>[], 'p': <String>[], 'n': <String>[]};
  String? current;
  final aliases = {
    'r': 'r',
    'representation': 'r',
    'what it looks like': 'r',
    'what it looks like (r)': 'r',
    'd': 'd',
    'description': 'd',
    'what they wrote': 'd',
    'what they wrote (d)': 'd',
    'p': 'p',
    'reality': 'p',
    'what it actually does': 'p',
    'what it actually does (p)': 'p',
    'n': 'n',
    'missing pieces': 'n',
    'missing pieces (n)': 'n',
  };
  for (final line in blob.split('\n')) {
    final idx = line.indexOf(':');
    if (idx > 0 && idx < 80) {
      final header = line.substring(0, idx).trim().toLowerCase();
      final rest = line.substring(idx + 1).trim();
      if (aliases.containsKey(header)) {
        current = aliases[header];
        if (rest.isNotEmpty) buckets[current]!.add(rest);
        continue;
      }
    }
    if (current != null) buckets[current]!.add(line.trimRight());
  }
  return {
    for (final k in buckets.keys) k: buckets[k]!.join('\n').trim(),
  };
}

class AzClceApp extends StatelessWidget {
  const AzClceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AZ-CLCE',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const FormPage(),
    );
  }
}

class FormPage extends StatefulWidget {
  const FormPage({super.key});

  @override
  State<FormPage> createState() => _FormPageState();
}

class _FormPageState extends State<FormPage> {
  final _r = TextEditingController();
  final _d = TextEditingController();
  final _p = TextEditingController();
  final _n = TextEditingController();
  Report? _report;
  bool _advanced = false;

  static const _sample = {
    'r': 'a blue login button that says submit',
    'd': 'the login form submits your name and password',
    'p': 'the login button submits your name and password',
    'n': 'forgot password link',
  };

  @override
  void dispose() {
    _r.dispose();
    _d.dispose();
    _p.dispose();
    _n.dispose();
    super.dispose();
  }

  void _run() {
    setState(() {
      _report = scoreLayers(_r.text, _d.text, _p.text, _n.text);
    });
  }

  void _fillSample() {
    _r.text = _sample['r']!;
    _d.text = _sample['d']!;
    _p.text = _sample['p']!;
    _n.text = _sample['n']!;
    _run();
  }

  Future<void> _importText() async {
    final controller = TextEditingController();
    final text = await showDialog<String>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('Import JSON or txt'),
          content: TextField(
            controller: controller,
            maxLines: 8,
            decoration: const InputDecoration(
              hintText: '{"r":"...","d":"...","p":"...","n":"..."}',
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, controller.text),
              child: const Text('Import'),
            ),
          ],
        );
      },
    );
    controller.dispose();
    if (text == null) return;
    try {
      final layers = parseLayersText(text);
      _r.text = layers['r'] ?? '';
      _d.text = layers['d'] ?? '';
      _p.text = layers['p'] ?? '';
      _n.text = layers['n'] ?? '';
      _run();
    } catch (err) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Import failed: $err')),
      );
    }
  }

  Future<void> _exportText() async {
    final report = _report ?? scoreLayers(_r.text, _d.text, _p.text, _n.text);
    final jsonOut = const JsonEncoder.withIndent('  ').convert({
      'r': _r.text,
      'd': _d.text,
      'p': _p.text,
      'n': _n.text,
      'triple': report.triple,
      'band': report.band,
      'kid_plain': report.kidPlain,
      'types': report.types,
    });
    final receipt = StringBuffer()
      ..writeln('AZ-CLCE receipt')
      ..writeln('===============')
      ..writeln('version: 0.2.0')
      ..writeln()
      ..writeln(limitation)
      ..writeln()
      ..writeln('What it looks like (R):')
      ..writeln('  ${_r.text.isEmpty ? "(empty)" : _r.text}')
      ..writeln()
      ..writeln('What they wrote (D):')
      ..writeln('  ${_d.text.isEmpty ? "(empty)" : _d.text}')
      ..writeln()
      ..writeln('What it actually does (P):')
      ..writeln('  ${_p.text.isEmpty ? "(empty)" : _p.text}')
      ..writeln()
      ..writeln('Missing pieces (N):')
      ..writeln('  ${_n.text.isEmpty ? "(empty)" : _n.text}')
      ..writeln()
      ..writeln('Score: ${report.triple.toStringAsFixed(4)}')
      ..writeln('Band: ${report.band}')
      ..writeln('Kid-plain:')
      ..writeln('  ${report.kidPlain}')
      ..writeln()
      ..writeln('Hash the JSON {r,d,p,n} with desktop `clce` for input_sha256.');
    final blob = '$jsonOut\n\n---\n\n$receipt';
    await Clipboard.setData(ClipboardData(text: blob));
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('Exported to clipboard'),
          content: SingleChildScrollView(child: SelectableText(blob)),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final report = _report;
    return Scaffold(
      appBar: AppBar(
        title: const Text('AZ-CLCE'),
        actions: [
          TextButton(
            onPressed: () => setState(() => _advanced = !_advanced),
            child: Text(_advanced ? 'Simple' : 'Advanced'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Cross-Layer Consistency Engine. Inconsistency, not intent.',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: kGold,
                  fontStyle: FontStyle.italic,
                ),
          ),
          const SizedBox(height: 8),
          const Text(limitation),
          const SizedBox(height: 16),
          TextField(
            controller: _r,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'What it looks like (R)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _d,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'What they wrote (D)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _p,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'What it actually does (P)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _n,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Missing pieces (N)',
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(onPressed: _run, child: const Text('Score')),
              OutlinedButton(onPressed: _fillSample, child: const Text('Fill sample')),
              OutlinedButton(onPressed: _importText, child: const Text('Import')),
              OutlinedButton(onPressed: _exportText, child: const Text('Export')),
            ],
          ),
          if (report != null) ...[
            const SizedBox(height: 16),
            Text(
              '${(report.triple * 100).round()}',
              style: const TextStyle(
                fontSize: 64,
                fontWeight: FontWeight.w700,
                color: kGold,
                height: 1,
              ),
            ),
            const SizedBox(height: 8),
            Text(report.kidPlain),
            if (_advanced) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('triple  ${report.triple.toStringAsFixed(4)}'),
                      Text('R↔D     ${report.rd.toStringAsFixed(4)}'),
                      Text('D↔P     ${report.dp.toStringAsFixed(4)}'),
                      Text('R↔P     ${report.rp.toStringAsFixed(4)}'),
                      Text('avg     ${report.avg.toStringAsFixed(4)}'),
                      Text('CLCE+   ${report.plus.toStringAsFixed(4)}'),
                      const SizedBox(height: 8),
                      Text('band: ${report.band}',
                          style: const TextStyle(color: kGold)),
                      const SizedBox(height: 8),
                      if (report.types.isEmpty)
                        const Text('No mismatch type matched.')
                      else
                        ...report.types.map((code) {
                          final primary = code == report.primary ? ' (primary)' : '';
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Text(
                              'Type $code ${typeLabels[code]}$primary\n${typeNotes[code]}',
                            ),
                          );
                        }),
                      const SizedBox(height: 8),
                      const Text(limitation, style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }
}
