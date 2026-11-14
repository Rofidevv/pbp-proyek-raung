import 'package:flutter/material.dart';

import 'screens/dasbor_sarpras_screen.dart';
import 'screens/daftar_laporan_screen.dart';
import 'screens/ruang_screen.dart';
import 'screens/status_publik_screen.dart';

void main() => runApp(const LaporFasApp());

class LaporFasApp extends StatelessWidget {
  const LaporFasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LaporFas',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo)),
      home: const Beranda(),
    );
  }
}

class Beranda extends StatefulWidget {
  const Beranda({super.key});

  @override
  State<Beranda> createState() => _BerandaState();
}

class _BerandaState extends State<Beranda> {
  int _tab = 0;

  // Detail Laporan dan Form Lapor dibuka lewat Navigator.push; enam tujuan terlalu banyak untuk nav bar.
  static const _tujuan = [
    (label: 'Ruang', ikon: Icons.qr_code_scanner),
    (label: 'Daftar', ikon: Icons.list_alt),
    (label: 'Sarpras', ikon: Icons.dashboard),
    (label: 'Publik', ikon: Icons.public),
  ];

  void _pilih(int i) => setState(() => _tab = i);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final lebar = constraints.maxWidth >= 600;
        // IndexedStack menjaga state tiap tab (ruang terpilih, laporan terpilih) saat pindah tab.
        final stack = IndexedStack(
          index: _tab,
          children: const [
            RuangScreen(),
            DaftarLaporanScreen(),
            DasborSarprasScreen(),
            StatusPublikScreen(),
          ],
        );
        if (lebar) {
          return Scaffold(
            body: Row(
              children: [
                NavigationRail(
                  selectedIndex: _tab,
                  onDestinationSelected: _pilih,
                  labelType: NavigationRailLabelType.all,
                  destinations: [
                    for (final t in _tujuan)
                      NavigationRailDestination(icon: Icon(t.ikon), label: Text(t.label)),
                  ],
                ),
                const VerticalDivider(width: 1),
                Expanded(child: stack),
              ],
            ),
          );
        }
        return Scaffold(
          body: stack,
          bottomNavigationBar: NavigationBar(
            selectedIndex: _tab,
            onDestinationSelected: _pilih,
            destinations: [
              for (final t in _tujuan) NavigationDestination(icon: Icon(t.ikon), label: t.label),
            ],
          ),
        );
      },
    );
  }
}
