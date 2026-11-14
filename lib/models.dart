enum StatusLaporan {
  menunggu('Menunggu'),
  diproses('Diproses'),
  selesai('Selesai'),
  ditutup('Ditutup');

  const StatusLaporan(this.label);
  final String label;
}

// Urutan dari rendah ke mendesak; index dipakai untuk mengurutkan antrean sarpras.
enum Urgensi {
  rendah('Rendah'),
  sedang('Sedang'),
  mendesak('Mendesak');

  const Urgensi(this.label);
  final String label;
}

// Urutan dari layak ke tidak layak; index dipakai LabelTingkat.
enum KelayakanRuang {
  layak('Layak'),
  adaLaporanTerbuka('Ada laporan terbuka'),
  tidakLayak('Tidak layak');

  const KelayakanRuang(this.label);
  final String label;
}

class Ruang {
  const Ruang({
    required this.kode,
    required this.gedung,
    required this.jadwalPakai,
    required this.statusKelayakan,
  });

  final String kode;
  final String gedung;
  final String jadwalPakai;
  final KelayakanRuang statusKelayakan;
}

class Laporan {
  const Laporan({
    required this.id,
    required this.ruang,
    required this.judul,
    required this.deskripsi,
    this.fotoUrl,
    required this.status,
    required this.urgensi,
    required this.nimPelapor,
    required this.dukungan,
    required this.dibuatPada,
  });

  final int id;
  final String ruang; // kode Ruang
  final String judul;
  final String deskripsi;
  final String? fotoUrl;
  final StatusLaporan status;
  final Urgensi urgensi;
  final String nimPelapor;
  final int dukungan;
  final DateTime dibuatPada;
}
