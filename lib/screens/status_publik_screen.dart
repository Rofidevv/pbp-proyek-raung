import 'package:flutter/material.dart';

import '../data_contoh.dart';
import '../models.dart';
import '../widgets/label_tingkat.dart';

class StatusPublikScreen extends StatelessWidget {
  const StatusPublikScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Status Publik')),
      body: ListView(
        children: [
          for (final r in ruangContoh)
            ListTile(
              title: Text(r.kode),
              subtitle: Text(
                '${r.gedung} · '
                '${laporanContoh.where((l) => l.ruang == r.kode && l.status != StatusLaporan.ditutup).length} laporan terbuka',
              ),
              trailing: LabelTingkat(r.statusKelayakan.label, tingkat: r.statusKelayakan.index),
            ),
        ],
      ),
    );
  }
}
