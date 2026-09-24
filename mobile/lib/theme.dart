import 'package:flutter/material.dart';

/// Matte black + gold Material 3 dark theme. No analytics.
const Color kMatteBlack = Color(0xFF0B0B0B);
const Color kSurface = Color(0xFF141414);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF8A7219);
const Color kIvory = Color(0xFFE8E0D0);

ThemeData buildLightTheme() {
  const scheme = ColorScheme.light(
    brightness: Brightness.light,
    primary: Color(0xFF6E5310),
    onPrimary: Color(0xFFFFFCF7),
    secondary: kGold,
    onSecondary: kMatteBlack,
    surface: Color(0xFFFFFCF7),
    onSurface: Color(0xFF1C1914),
    error: Color(0xFF9D2C2C),
    onError: Color(0xFFFFFCF7),
  );
  return _theme(scheme, const Color(0xFFF6F3EC), const Color(0xFF1C1914));
}

ThemeData buildAppTheme() {
  const scheme = ColorScheme.dark(
    brightness: Brightness.dark,
    primary: kGold,
    onPrimary: kMatteBlack,
    secondary: kGoldDim,
    onSecondary: kIvory,
    surface: kSurface,
    onSurface: kIvory,
    error: Color(0xFFB54A4A),
    onError: kIvory,
  );
  return _theme(scheme, kMatteBlack, kGold);
}

ThemeData _theme(ColorScheme scheme, Color scaffold, Color title) {
  return ThemeData(
    useMaterial3: true,
    brightness: scheme.brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: title,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0x33C9A227)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.brightness == Brightness.dark
          ? const Color(0xFF1A1A1A)
          : const Color(0xFFFFFFFF),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
    segmentedButtonTheme: SegmentedButtonThemeData(
      style: ButtonStyle(
        foregroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kMatteBlack : kIvory;
        }),
        backgroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kGold : kSurface;
        }),
      ),
    ),
  );
}
