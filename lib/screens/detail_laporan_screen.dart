import 'package:flutter/material.dart';

import '../models.dart';

/// Isi detail tanpa Scaffold; dipakai di panel kanan Daftar dan di halaman push.
class DetailLaporan extends StatelessWidget {
  const DetailLaporan({super.key, required this.laporan});

  final Laporan laporan;

  @override
  Widget build(BuildContext context) {
    final d = laporan.dibuatPada;
    Widget baris(String label, String isi) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            children: [
              SizedBox(width: 100, child: Text(label)),
              Expanded(child: Text(isi)),
            ],
          ),
        );
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(laporan.judul, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        baris('Ruang', laporan.ruang),
        baris('Status', laporan.status.label),
        baris('Urgensi', laporan.urgensi.label),
        baris('Dukungan', '${laporan.dukungan}'),
        baris('Dibuat', '${d.day}/${d.month}/${d.year}'),
        const SizedBox(height: 12),
        Text(laporan.deskripsi),
      ],
    );
  }
}

class DetailLaporanScreen extends StatelessWidget {
  const DetailLaporanScreen({super.key, required this.laporan});

  final Laporan laporan;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Detail Laporan')),
      body: DetailLaporan(laporan: laporan),
    );
  }
}
