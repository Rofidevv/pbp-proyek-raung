# LaporFas - Repository Proyek Kelompok raung
## 1. Nama dan Anggota

- **Nama kelompok:** raung
- **Nama aplikasi:** LaporFas
- **Mode pengerjaan:** individu (solo)
- **Repository:** <https://github.com/Rofidevv/pbp-proyek-raung>

| Nama | NIM | Akun GitHub |
| --- | --- | --- |
| ROFI'UL KHAQIM | 243401009 | [Rofidevv](https://github.com/Rofidevv) |

## 2. Ringkasan Usulan Proyek v2

Kerusakan fasilitas ruang kelas tidak punya jalur pelaporan yang jelas. Laporan disampaikan lisan atau lewat chat informal yang tidak tercatat, sehingga mudah hilang, tidak terlacak, dan tidak ada kepastian ditindaklanjuti. Contoh yang saya alami: AC ruang kelas tidak bisa swing dan LCD proyektor tidak bisa dimatikan, tetapi tidak ada jalur lapor yang jelas.

LaporFas menggabungkan banyak keluhan atas kerusakan yang sama menjadi satu laporan:
- mahasiswa memindai QR di pintu ruang untuk melihat laporan yang sudah ada, lalu menekan **"saya juga mengalami"** atau membuat laporan baru dengan foto;
- satu NIM hanya boleh memberi satu dukungan per laporan, sehingga tidak ada laporan ganda;
- petugas sarana (sarpras) menetapkan urgensi final, menindaklanjuti secara tercatat, dan bekerja dari antrean terurut prioritas;
- pelapor menerima kabar status, memverifikasi hasil perbaikan, lalu menutup laporannya sendiri.

Alur: pindai QR -> daftar laporan ruang -> ikut melapor atau lapor baru + foto -> urgensi awal otomatis dan urgensi final sarpras -> tindak lanjut -> kabar status -> pelapor verifikasi dan menutup.

Platform: **Android** untuk mahasiswa di depan ruang (QR, kamera, kabar status); **desktop** untuk sarpras (antrean prioritas, rekap per gedung, cetak QR); **web publik baca-saja** untuk status ruang dan daftar laporan tanpa instalasi.

## 3. Kontrak Lima Unsur

1. **CRUD daftar-detail-form** - mahasiswa menambah, melihat daftar dan detail, mengubah, dan menghapus laporan kerusakannya sendiri pada data Laporan.
2. **API backend (FastAPI)** - `GET /laporan`, `POST /laporan`, `GET /laporan/{id}`, `PUT /laporan/{id}`, `PATCH /laporan/{id}/status`, `DELETE /laporan/{id}`; endpoint pendukung: `GET /ruang/{kode}/laporan`, `POST /laporan/{id}/dukungan`, `POST /laporan/{id}/tindak-lanjut`, `POST /laporan/{id}/tutup`.
3. **Layout adaptif** - di HP daftar satu kolom dengan bottom navigation; di layar lebar dua kolom daftar-detail berdampingan; desktop sarpras berupa tabel antrean.
4. **State lintas layar** - filter status (Menunggu/Diproses/Selesai/Ditutup), filter urgensi, dan ruang aktif hasil pindai QR dipakai bersama di layar Daftar, Detail Ruang, dan Status.
5. **Penyimpanan lokal** - cache daftar terakhir, pilihan filter, dan antrean lapor luring yang dikirim ulang saat daring.

## 4. Batasan dan Backlog Awal

**Batasan (pagu):** 3 entitas dan 6 layar.

- Entitas: **Laporan** (judul, ruang, foto, status, urgensi), **Ruang** (kodeQR, gedung, jadwalPakai, statusKelayakan), **TindakLanjut** (idLaporan, catatanSarpras, tanggal, ditutupOlehPelapor).
- Layar: (1) Pindai QR/Detail Ruang, (2) Daftar Laporan, (3) Detail Laporan, (4) Form Lapor, (5) Dasbor Sarpras, (6) Status Publik Web.
- Backend FastAPI. Frontend Flutter. Tidak ada autentikasi penuh, notifikasi push, atau fitur di luar enam layar.

**Backlog awal**.

| No | Butir backlog | Unsur kontrak |
| --- | --- | --- |
| R-01 | Sebagai mahasiswa, saya ingin memindai QR ruang dan melihat laporan yang sudah ada di ruang itu, supaya saya tidak membuat laporan ganda. | State lintas layar; layout adaptif |
| R-02 | Sebagai mahasiswa, saya ingin membuat laporan baru dengan foto dan deskripsi, supaya kerusakan tercatat lengkap. | CRUD (create) |
| R-03 | Sebagai mahasiswa, saya ingin menekan "saya juga mengalami" sekali per laporan, supaya dukungan terhitung tanpa laporan ganda. | API (POST dukungan, unik per NIM) |
| R-04 | Sebagai mahasiswa, saya ingin mengubah atau menghapus laporan saya selama statusnya Menunggu, supaya saya bisa memperbaiki kesalahan. | CRUD (update, delete) |
| R-05 | Sebagai pengembang, saya ingin lima endpoint inti FastAPI berjalan, supaya aplikasi Flutter punya sumber data nyata. | API backend sendiri |
| R-06 | Sebagai pengguna, saya ingin filter status, urgensi, dan ruang aktif bertahan saat berpindah layar, supaya konteks tidak hilang. | State lintas layar |
| R-07 | Sebagai sarpras, saya ingin daftar dan detail tampil berdampingan di layar lebar dan satu kolom di HP, supaya pekerjaan cepat di desktop dan tetap nyaman di HP. | Layout adaptif |
| R-08 | Sebagai mahasiswa, saya ingin daftar terakhir tetap terbuka saat luring dan laporan tertunda terkirim saat daring, supaya laporan tidak hilang. | Penyimpanan lokal |