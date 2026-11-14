import 'package:flutter/material.dart';

import '../data_contoh.dart';
import '../models.dart';
import 'detail_laporan_screen.dart';

class DasborSarprasScreen extends StatelessWidget {
  const DasborSarprasScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final antrean = laporanContoh
        .where((l) => l.status == StatusLaporan.menunggu || l.status == StatusLaporan.diproses)
        .toList()
      ..sort((a, b) {
        final u = b.urgensi.index.compareTo(a.urgensi.index);
        return u != 0 ? u : b.dukungan.compareTo(a.dukungan);
      });
    return Scaffold(
      appBar: AppBar(title: const Text('Dasbor Sarpras')),
      body: SingleChildScrollView(
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            showCheckboxColumn: false,
            columns: const [
              DataColumn(label: Text('Ruang')),
              DataColumn(label: Text('Judul')),
              DataColumn(label: Text('Urgensi')),
              DataColumn(label: Text('Dukungan'), numeric: true),
              DataColumn(label: Text('Status')),
            ],
            rows: [
              for (final l in antrean)
                DataRow(
                  onSelectChanged: (_) => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => DetailLaporanScreen(laporan: l)),
                  ),
                  cells: [
                    DataCell(Text(l.ruang)),
                    DataCell(Text(l.judul)),
                    DataCell(Text(l.urgensi.label)),
                    DataCell(Text('${l.dukungan}')),
                    DataCell(Text(l.status.label)),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
