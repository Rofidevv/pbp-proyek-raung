import 'package:flutter/material.dart';

import '../data_contoh.dart';
import '../models.dart';
import '../widgets/label_tingkat.dart';
import 'detail_laporan_screen.dart';
import 'form_lapor_screen.dart';

class RuangScreen extends StatefulWidget {
  const RuangScreen({super.key});

  @override
  State<RuangScreen> createState() => _RuangScreenState();
}

class _RuangScreenState extends State<RuangScreen> {
  Ruang _aktif = ruangContoh.first;

  @override
  Widget build(BuildContext context) {
    final terbuka = laporanContoh
        .where((l) => l.ruang == _aktif.kode && l.status != StatusLaporan.ditutup)
        .toList();
    return Scaffold(
      appBar: AppBar(title: const Text('Pindai QR / Detail Ruang')),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Pengganti pindai QR (R-01); tetap jadi fallback di web/desktop.
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Text('Pilih ruang'),
                const SizedBox(width: 16),
                DropdownButton<Ruang>(
                  value: _aktif,
                  items: [
                    for (final r in ruangContoh) DropdownMenuItem(value: r, child: Text(r.kode)),
                  ],
                  onChanged: (r) => setState(() => _aktif = r!),
                ),
              ],
            ),
          ),
          Card(
            margin: const EdgeInsets.all(16),
            child: ListTile(
              title: Text(_aktif.kode),
              subtitle: Text('${_aktif.gedung}\n${_aktif.jadwalPakai}'),
              isThreeLine: true,
              trailing: LabelTingkat(_aktif.statusKelayakan.label, tingkat: _aktif.statusKelayakan.index),
            ),
          ),
          Expanded(
            child: terbuka.isEmpty
                ? const Center(child: Text('Belum ada laporan terbuka di ruang ini.'))
                : ListView(
                    children: [
                      for (final l in terbuka)
                        ListTile(
                          title: Text(l.judul),
                          subtitle: Text('${l.status.label} · ${l.dukungan} dukungan'),
                          trailing: LabelTingkat(l.urgensi.label, tingkat: l.urgensi.index),
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => DetailLaporanScreen(laporan: l)),
                          ),
                        ),
                    ],
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        icon: const Icon(Icons.add),
        label: const Text('Lapor baru'),
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => FormLaporScreen(ruang: _aktif.kode)),
        ),
      ),
    );
  }
}
