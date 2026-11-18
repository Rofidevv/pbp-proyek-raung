# Backend LaporFas

API FastAPI untuk laporan kerusakan ruang kelas LaporFas. Alamat publik: <https://pbp-proyek-raung.onrender.com>, dokumentasi interaktif di <https://pbp-proyek-raung.onrender.com/docs>.

## Stack

- FastAPI dan SQLAlchemy 2.
- Online: Postgres di Neon, server di Render.
- Lokal: file SQLite `laporfas.db` di folder ini, dipakai otomatis bila `DATABASE_URL` tidak diisi.

## Perintah

Jalankan dari folder `backend/` dengan venv aktif (`python -m venv .venv`, lalu `source .venv/Scripts/activate` di Git Bash atau `.venv\Scripts\activate` di cmd).

| Keperluan | Perintah |
| --- | --- |
| Pasang dependensi | `pip install -r requirements.txt` |
| Menjalankan server | `uvicorn app.main:app --reload` |
| Mengisi data contoh (menghapus data lama) | `python -m app.seed` |
| Menjalankan tes | `python -m pytest` |

Tes memakai database SQLite sementara, jadi tidak menyentuh data di `.env`.

## Konfigurasi `.env`

Salin `.env.example` menjadi `.env`, lalu isi `DATABASE_URL` dengan connection string Neon. Tanpa `.env`, server memakai SQLite lokal. File `.env` dan `*.db` ada di `.gitignore`, jadi tidak ikut ter-commit.

## Model Data

Ruang (1) -> Laporan (banyak) -> TindakLanjut (banyak).

| Entitas | Field | Catatan |
| --- | --- | --- |
| Ruang | `kode`, `gedung`, `jadwal_pakai`, `status_kelayakan`, `dibuat_pada` | `kode` adalah isi QR di pintu, misalnya `VL 4A`. |
| Laporan | `id`, `ruang`, `judul`, `deskripsi`, `foto_url`, `status`, `urgensi`, `nim_pelapor`, `dukungan`, `dibuat_pada`, `diubah_pada` | `ruang` menunjuk `Ruang.kode`. Server menyimpan daftar NIM pendukung, respons hanya memuat jumlahnya (`dukungan`). |
| TindakLanjut | `id`, `laporan_id`, `catatan_sarpras`, `ditutup_oleh_pelapor`, `dibuat_pada` | Ikut terhapus saat laporannya dihapus. |

Nilai tetap:

- `status`: `Menunggu`, `Diproses`, `Selesai`, `Ditutup`.
- `urgensi`: `Rendah`, `Sedang`, `Mendesak` (bawaan `Sedang`).
- `status_kelayakan`: `layak`, `ada_laporan_terbuka`, `tidak_layak`.
- Waktu dalam WIB tanpa offset, contoh `2026-11-18T22:10:00.123456`.

Pesan galat ada di field `detail`, contoh `{"detail": "Laporan 9999 tidak ada"}`.

## Endpoint

Semua endpoint dipegang oleh ROFI'UL KHAQIM (mode individu).

| # | Metode dan alamat | Contoh permintaan | Contoh jawaban | Kode gagal | Pemegang |
| --- | --- | --- | --- | --- | --- |
| 1 | `GET /ruang` | | 200, `[{"kode": "KL 2A", "gedung": "Gedung K", "jadwal_pakai": "...", "status_kelayakan": "ada_laporan_terbuka", "dibuat_pada": "..."}]`, urut `kode` | | ROFI'UL KHAQIM |
| 2 | `GET /ruang/{kode}/laporan` | `GET /ruang/VL 4A/laporan` | 200, daftar laporan ruang itu, terbaru dulu | 404 ruang tidak ada | ROFI'UL KHAQIM |
| 3 | `GET /laporan` | `GET /laporan?status=Menunggu&urgensi=Mendesak&ruang=VL 4A&q=proyektor&urut=prioritas` | 200, daftar laporan. `urut`: `terbaru` (bawaan), `terlama`, `prioritas` (urgensi lalu dukungan). `q` mencari di judul dan deskripsi tanpa membedakan huruf besar. | 422 nilai `status`, `urgensi`, atau `urut` tidak dikenal | ROFI'UL KHAQIM |
| 4 | `POST /laporan` | `{"ruang": "VL 4A", "judul": "Proyektor mati", "deskripsi": "Tidak menyala sejak pagi.", "urgensi": "Mendesak", "nim_pelapor": "243401009"}` | 201, laporan lengkap dengan `id`, `status: "Menunggu"`, `dukungan: 1`, `tindak_lanjut: []` | 422 field kosong, judul lebih dari 120 huruf, NIM bukan 9 angka, atau ruang tidak ada | ROFI'UL KHAQIM |
| 5 | `GET /laporan/{id}` | `GET /laporan/1` | 200, laporan lengkap dengan `tindak_lanjut` terbaru dulu | 404 id tidak ada; 422 id bukan angka | ROFI'UL KHAQIM |
| 6 | `PUT /laporan/{id}` | `{"ruang": "VL 4A", "judul": "Proyektor mati total", "deskripsi": "Lampu indikator juga mati.", "urgensi": "Mendesak"}` | 200, laporan dengan `diubah_pada` baru | 404; 409 status bukan Menunggu; 422 isi tidak valid | ROFI'UL KHAQIM |
| 7 | `PATCH /laporan/{id}/status` | `{"status": "Diproses", "urgensi": "Mendesak"}` (`urgensi` boleh dilewati) | 200, laporan dengan status baru | 404; 422 status tidak dikenal | ROFI'UL KHAQIM |
| 8 | `DELETE /laporan/{id}` | `DELETE /laporan/1` | 200, laporan yang dihapus; tindak lanjutnya ikut terhapus | 404; 409 status bukan Menunggu | ROFI'UL KHAQIM |
| 9 | `POST /laporan/{id}/dukungan` | `{"nim": "249900001"}` | 201, laporan dengan `dukungan` bertambah 1 | 404; 409 NIM sudah mendukung (termasuk pelapor); 422 NIM bukan 9 angka | ROFI'UL KHAQIM |
| 10 | `GET /laporan/{id}/tindak-lanjut` | `GET /laporan/2/tindak-lanjut` | 200, `[{"id": 1, "laporan_id": 2, "catatan_sarpras": "...", "ditutup_oleh_pelapor": false, "dibuat_pada": "..."}]`, terbaru dulu | 404 | ROFI'UL KHAQIM |
| 11 | `POST /laporan/{id}/tindak-lanjut` | `{"catatan_sarpras": "Teknisi dijadwalkan datang Kamis."}` | 201, tindak lanjut baru; status laporan tidak berubah | 404; 422 catatan kosong | ROFI'UL KHAQIM |
| 12 | `POST /laporan/{id}/tutup` | `{"nim": "243401009"}` | 200, laporan berstatus `Ditutup` dengan tindak lanjut baru `ditutup_oleh_pelapor: true` | 404; 403 NIM bukan pelapor; 409 status belum Selesai | ROFI'UL KHAQIM |
| 13 | `GET /ringkasan` | | 200, `{"total": 12, "per_status": {"Menunggu": 4, ...}, "per_urgensi": {...}, "terbuka_per_gedung": {"Gedung K": 2, "Gedung V": 5}, "dibuat_pekan_ini": 3}` | | ROFI'UL KHAQIM |

## Catatan Render

Layanan gratis Render tidur sesudah sekitar 15 menit tanpa permintaan, jadi permintaan pertama bisa makan waktu sampai sekitar 1 menit. Buka `/docs` sekali sebelum pemeriksaan supaya server sudah bangun.
