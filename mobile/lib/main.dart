import 'package:flutter/material.dart';

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
  );
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

  @override
  Widget build(BuildContext context) {
    final report = _report;
    return Scaffold(
      appBar: AppBar(title: const Text('AZ-CLCE')),
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
              labelText: 'R — Representation',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _d,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'D — Description',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _p,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'P — Reality',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _n,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'N — Missing expected (optional)',
            ),
          ),
          const SizedBox(height: 16),
          FilledButton(onPressed: _run, child: const Text('Score / Classify')),
          if (report != null) ...[
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
      ),
    );
  }
}
