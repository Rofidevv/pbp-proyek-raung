import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:raung/main.dart';

void main() {
  testWidgets('enam layar bisa dibuka', (tester) async {
    await tester.pumpWidget(const LaporFasApp());
    expect(find.text('Pindai QR / Detail Ruang'), findsOneWidget);

    await tester.tap(find.text('Lapor baru'));
    await tester.pumpAndSettle();
    expect(find.text('Form Lapor'), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.list_alt));
    await tester.pumpAndSettle();
    expect(find.text('Daftar Laporan'), findsOneWidget);
    // VL 4C: tidak ada di tab Ruang (aktif VL 4A), jadi finder tidak ganda.
    await tester.tap(find.text('Lampu depan mati'));
    await tester.pumpAndSettle();
    expect(find.text('Detail Laporan'), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.dashboard));
    await tester.pumpAndSettle();
    expect(find.text('Dasbor Sarpras'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.public));
    await tester.pumpAndSettle();
    expect(find.text('Status Publik'), findsOneWidget);
  });

  testWidgets('Daftar-Detail berdampingan pada lebar >= 840', (tester) async {
    tester.view.physicalSize = const Size(1400, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const LaporFasApp());
    await tester.tap(find.byIcon(Icons.list_alt));
    await tester.pumpAndSettle();
    expect(find.text('Tombol power tidak merespons sejak kuliah pertama.'), findsOneWidget);

    await tester.tap(find.text('Lampu depan mati'));
    await tester.pumpAndSettle();
    expect(find.text('Dua lampu dekat papan tulis mati.'), findsOneWidget);
    expect(find.text('Detail Laporan'), findsNothing);
  });

  testWidgets('Daftar satu panel pada lebar < 600', (tester) async {
    tester.view.physicalSize = const Size(400, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const LaporFasApp());
    await tester.tap(find.byIcon(Icons.list_alt));
    await tester.pumpAndSettle();
    expect(find.text('Daftar Laporan'), findsOneWidget);
    expect(find.text('Tombol power tidak merespons sejak kuliah pertama.'), findsNothing);
  });
}
