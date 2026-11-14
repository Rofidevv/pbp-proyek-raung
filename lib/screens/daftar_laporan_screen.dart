import 'package:flutter/material.dart';

import '../data_contoh.dart';
import '../models.dart';
import 'detail_laporan_screen.dart';

class DaftarLaporanScreen extends StatefulWidget {
  const DaftarLaporanScreen({super.key});

  @override
  State<DaftarLaporanScreen> createState() => _DaftarLaporanScreenState();
}

class _DaftarLaporanScreenState extends State<DaftarLaporanScreen> {
  Laporan _terpilih = laporanContoh.first;

  Widget _daftar({required bool berdampingan}) {
    return ListView(
      children: [
        for (final l in laporanContoh)
          ListTile(
            title: Text(l.judul),
            subtitle: Text('${l.ruang} · ${l.status.label} · ${l.urgensi.label}'),
            selected: berdampingan && l == _terpilih,
            onTap: berdampingan
                ? () => setState(() => _terpilih = l)
                : () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => DetailLaporanScreen(laporan: l)),
                    ),
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Daftar Laporan')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          // Kartu #18: >= 840 berdampingan; di bawahnya (termasuk 600-839) satu panel.
          if (constraints.maxWidth >= 840) {
            return Row(
              children: [
                SizedBox(width: 360, child: _daftar(berdampingan: true)),
                const VerticalDivider(width: 1),
                Expanded(child: DetailLaporan(laporan: _terpilih)),
              ],
            );
          }
          return _daftar(berdampingan: false);
        },
      ),
    );
  }
}
