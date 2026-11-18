from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, sekarang
from .models import Kelayakan, Laporan, Ruang, Status, TindakLanjut, Urgensi

PELAPOR = "243401009"


def nim_palsu(n: int) -> str:
    return f"2499000{n:02d}"


RUANG = [
    ("VL 4A", "Gedung V", "Senin 08.00-09.40; Rabu 13.00-14.40", Kelayakan.ADA_LAPORAN_TERBUKA),
    ("VL 4B", "Gedung V", "Selasa 10.00-11.40", Kelayakan.LAYAK),
    ("VL 4C", "Gedung V", "Kamis 07.00-09.30", Kelayakan.TIDAK_LAYAK),
    ("VL 3A", "Gedung V", "Senin 10.00-11.40; Kamis 13.00-14.40", Kelayakan.ADA_LAPORAN_TERBUKA),
    ("VL 3B", "Gedung V", "Jumat 08.00-10.30", Kelayakan.LAYAK),
    ("KL 2A", "Gedung K", "Selasa 13.00-15.30; Rabu 08.00-09.40", Kelayakan.ADA_LAPORAN_TERBUKA),
]

# (ruang, judul, deskripsi, status, urgensi, pelapor, jumlah dukungan, umur dalam jam, tindak lanjut)
LAPORAN = [
    ("VL 4A", "LCD proyektor tidak bisa dimatikan", "Tombol power tidak merespons sejak kuliah pertama.",
     Status.MENUNGGU, Urgensi.MENDESAK, PELAPOR, 7, 3, []),
    ("VL 4A", "AC tidak bisa swing", "Arah angin AC macet ke satu sisi.",
     Status.DIPROSES, Urgensi.SEDANG, PELAPOR, 3, 24 * 5, ["Teknisi AC dijadwalkan cek motor swing hari Kamis."]),
    ("VL 4C", "Kursi patah 4 buah", "Empat kursi barisan belakang patah kakinya.",
     Status.MENUNGGU, Urgensi.RENDAH, PELAPOR, 1, 24 * 9, ["Sudah dicatat, menunggu stok kursi pengganti dari gudang."]),
    ("VL 4C", "Lampu depan mati", "Dua lampu dekat papan tulis mati.",
     Status.MENUNGGU, Urgensi.MENDESAK, PELAPOR, 5, 5, []),
    ("VL 4B", "Stop kontak longgar", "Colokan di meja dosen mudah lepas.",
     Status.DITUTUP, Urgensi.RENDAH, PELAPOR, 2, 24 * 20,
     ["Stop kontak meja dosen diganti baru.", "Ditutup oleh pelapor sesudah memeriksa hasil perbaikan"]),
    ("VL 3A", "Gambar proyektor buram", "Tulisan di slide tidak terbaca dari baris tengah ke belakang.",
     Status.DIPROSES, Urgensi.SEDANG, nim_palsu(1), 4, 24 * 3, ["Lensa dibersihkan, fokus masih kurang. Lampu proyektor dipesan."]),
    ("VL 3A", "Kunci pintu rusak", "Pintu tidak bisa dikunci dari luar setelah kelas sore.",
     Status.SELESAI, Urgensi.MENDESAK, nim_palsu(2), 2, 24 * 12, ["Silinder kunci diganti, kunci baru dititipkan ke satpam."]),
    ("KL 2A", "Kabel HDMI tidak terdeteksi", "Laptop sudah dicolok tapi proyektor menampilkan no signal.",
     Status.MENUNGGU, Urgensi.SEDANG, nim_palsu(3), 3, 2, []),
    ("KL 2A", "Gorden sobek", "Gorden jendela kiri sobek, layar silau saat siang.",
     Status.DIPROSES, Urgensi.RENDAH, nim_palsu(4), 1, 24 * 7, ["Ukuran jendela sudah diukur untuk gorden baru."]),
    ("VL 3B", "Kipas angin berisik", "Kipas di plafon berbunyi keras dan bergetar.",
     Status.SELESAI, Urgensi.SEDANG, PELAPOR, 2, 24 * 15, ["Baut dudukan kipas dikencangkan dan baling-baling diseimbangkan."]),
    ("VL 4B", "Papan tulis bernoda", "Bekas spidol permanen tidak bisa dihapus.",
     Status.DITUTUP, Urgensi.RENDAH, nim_palsu(5), 1, 24 * 18,
     ["Papan dibersihkan dengan cairan pembersih khusus.", "Ditutup oleh pelapor sesudah memeriksa hasil perbaikan"]),
    ("KL 2A", "Stop kontak dinding goyang", "Stop kontak dekat jendela goyang dan kadang memercikkan api.",
     Status.DITUTUP, Urgensi.MENDESAK, nim_palsu(6), 2, 24 * 21,
     ["Stop kontak dicabut dari dinding dan diganti.", "Ditutup oleh pelapor sesudah memeriksa hasil perbaikan"]),
]


def isi(db: Session) -> None:
    kini = sekarang()
    for kode, gedung, jadwal, kelayakan in RUANG:
        db.add(Ruang(kode=kode, gedung=gedung, jadwal_pakai=jadwal, status_kelayakan=kelayakan,
                     dibuat_pada=kini - timedelta(days=30)))
    db.flush()
    nomor = 10
    for ruang, judul, deskripsi, status, urgensi, pelapor, dukungan, umur, catatan in LAPORAN:
        dibuat = kini - timedelta(hours=umur)
        pendukung = [pelapor]
        while len(pendukung) < dukungan:
            nomor += 1
            pendukung.append(nim_palsu(nomor))
        lap = Laporan(ruang=ruang, judul=judul, deskripsi=deskripsi, status=status, urgensi=urgensi,
                      nim_pelapor=pelapor, pendukung=pendukung, dibuat_pada=dibuat,
                      diubah_pada=dibuat + timedelta(days=len(catatan)))
        for i, teks in enumerate(catatan, start=1):
            lap.tindak_lanjut.append(TindakLanjut(
                catatan_sarpras=teks,
                ditutup_oleh_pelapor=teks.startswith("Ditutup oleh pelapor"),
                dibuat_pada=dibuat + timedelta(days=i),
            ))
        db.add(lap)
    db.commit()


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        isi(db)
        r, l, t = (db.scalar(select(func.count()).select_from(m)) for m in (Ruang, Laporan, TindakLanjut))
    print(f"Data contoh terisi: {r} ruang, {l} laporan, {t} tindak lanjut")


if __name__ == "__main__":
    main()
