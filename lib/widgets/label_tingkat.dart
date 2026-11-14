import 'package:flutter/material.dart';

/// Motif identitas LaporFas: satu-satunya tempat warna dipakai.
/// Teks selalu ikut tampil, jadi informasinya tidak bergantung pada warna saja.
class LabelTingkat extends StatelessWidget {
  const LabelTingkat(this.teks, {super.key, required this.tingkat});

  final String teks;

  /// 0 = biasa, 1 = perlu perhatian, 2 = mendesak. Sama dengan `index` Urgensi dan KelayakanRuang.
  final int tingkat;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final (latar, isi) = switch (tingkat) {
      2 => (cs.errorContainer, cs.onErrorContainer),
      1 => (cs.tertiaryContainer, cs.onTertiaryContainer),
      _ => (cs.surfaceContainerHighest, cs.onSurfaceVariant),
    };
    return DecoratedBox(
      decoration: BoxDecoration(color: latar, borderRadius: BorderRadius.circular(4)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        child: Text(teks, style: Theme.of(context).textTheme.labelMedium?.copyWith(color: isi)),
      ),
    );
  }
}
