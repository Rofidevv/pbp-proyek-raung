from sqlalchemy import func, select

from app import seed
from app.database import Base, SessionLocal, engine
from app.models import TindakLanjut

from conftest import buat


def test_buat_laporan(klien):
    lap = buat(klien)
    assert {"id", "dibuat_pada", "diubah_pada"} <= lap.keys()
    assert lap["status"] == "Menunggu"
    assert lap["dukungan"] == 1
    assert lap["urgensi"] == "Sedang"
    assert "pendukung" not in lap


def test_buat_laporan_tidak_valid(klien):
    dasar = {"ruang": "VL 4A", "judul": "Ok", "deskripsi": "Ok", "nim_pelapor": "243401009"}
    assert klien.post("/laporan", json={**dasar, "judul": "   "}).status_code == 422
    assert klien.post("/laporan", json={**dasar, "judul": "x" * 121}).status_code == 422
    r = klien.post("/laporan", json={**dasar, "ruang": "ZZ 9"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Ruang ZZ 9 tidak ada"
    assert klien.post("/laporan", json={**dasar, "nim_pelapor": "abc"}).status_code == 422


def test_laporan_tidak_ada(klien):
    assert klien.get("/laporan/9999").status_code == 404
    assert klien.get("/laporan/abc").status_code == 422


def test_detail_memuat_tindak_lanjut_terbaru_dulu(klien):
    lap = buat(klien)
    for teks in ("pertama", "kedua"):
        assert klien.post(f"/laporan/{lap['id']}/tindak-lanjut", json={"catatan_sarpras": teks}).status_code == 201
    detail = klien.get(f"/laporan/{lap['id']}").json()
    assert [t["catatan_sarpras"] for t in detail["tindak_lanjut"]] == ["kedua", "pertama"]
    assert detail["status"] == "Menunggu"


def test_ubah_laporan(klien):
    lap = buat(klien)
    r = klien.put(f"/laporan/{lap['id']}", json={"ruang": "KL 1A", "judul": "Judul baru", "deskripsi": "Baru"})
    assert r.status_code == 200
    assert r.json()["judul"] == "Judul baru"
    assert r.json()["ruang"] == "KL 1A"
    assert r.json()["diubah_pada"] > lap["diubah_pada"]
    assert klien.put("/laporan/9999", json={"ruang": "VL 4A", "judul": "a", "deskripsi": "b"}).status_code == 404


def test_status_bukan_menunggu_mengunci_ubah_dan_hapus(klien):
    lap = buat(klien)
    r = klien.patch(f"/laporan/{lap['id']}/status", json={"status": "Diproses", "urgensi": "Mendesak"})
    assert r.status_code == 200
    assert (r.json()["status"], r.json()["urgensi"]) == ("Diproses", "Mendesak")
    assert klien.patch(f"/laporan/{lap['id']}/status", json={"status": "Hilang"}).status_code == 422
    assert klien.patch("/laporan/9999/status", json={"status": "Selesai"}).status_code == 404
    body = {"ruang": "VL 4A", "judul": "a", "deskripsi": "b"}
    assert klien.put(f"/laporan/{lap['id']}", json=body).status_code == 409
    assert klien.delete(f"/laporan/{lap['id']}").status_code == 409


def test_hapus_ikut_menghapus_tindak_lanjut(klien):
    lap = buat(klien)
    klien.post(f"/laporan/{lap['id']}/tindak-lanjut", json={"catatan_sarpras": "dicek"})
    r = klien.delete(f"/laporan/{lap['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == lap["id"]
    assert klien.get(f"/laporan/{lap['id']}").status_code == 404
    assert klien.get(f"/laporan/{lap['id']}/tindak-lanjut").status_code == 404
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(TindakLanjut)) == 0


def test_tindak_lanjut_gagal(klien):
    assert klien.get("/laporan/9999/tindak-lanjut").status_code == 404
    assert klien.post("/laporan/9999/tindak-lanjut", json={"catatan_sarpras": "x"}).status_code == 404
    lap = buat(klien)
    assert klien.post(f"/laporan/{lap['id']}/tindak-lanjut", json={"catatan_sarpras": ""}).status_code == 422


def test_filter_cari_dan_urut(klien):
    a = buat(klien, judul="Lampu mati", urgensi="Rendah")
    b = buat(klien, judul="AC bocor", deskripsi="Air menetes ke PROYEKTOR", urgensi="Mendesak")
    c = buat(klien, judul="Proyektor buram", ruang="KL 1A")
    klien.patch(f"/laporan/{a['id']}/status", json={"status": "Diproses"})

    ids = lambda url: [l["id"] for l in klien.get(url).json()]
    assert ids("/laporan?status=Menunggu") == [c["id"], b["id"]]
    assert ids("/laporan?ruang=KL 1A") == [c["id"]]
    assert set(ids("/laporan?q=proyektor")) == {b["id"], c["id"]}
    assert ids("/laporan?urut=prioritas") == [b["id"], c["id"], a["id"]]
    assert ids("/laporan?urut=terlama") == ids("/laporan?urut=terbaru")[::-1]
    assert klien.get("/laporan?status=Hilang").status_code == 422
    assert klien.get("/laporan?urut=acak").status_code == 422


def test_dukungan_sekali_per_nim(klien):
    lap = buat(klien)
    url = f"/laporan/{lap['id']}/dukungan"
    r = klien.post(url, json={"nim": "249900001"})
    assert r.status_code == 201
    assert r.json()["dukungan"] == 2
    assert klien.post(url, json={"nim": "249900001"}).status_code == 409
    assert klien.post(url, json={"nim": "243401009"}).status_code == 409
    assert klien.post(url, json={"nim": "12"}).status_code == 422
    assert klien.post("/laporan/9999/dukungan", json={"nim": "249900001"}).status_code == 404


def test_tutup_oleh_pelapor(klien):
    lap = buat(klien)
    url = f"/laporan/{lap['id']}/tutup"
    assert klien.post(url, json={"nim": "243401009"}).status_code == 409
    klien.patch(f"/laporan/{lap['id']}/status", json={"status": "Selesai"})
    assert klien.post(url, json={"nim": "249900001"}).status_code == 403
    r = klien.post(url, json={"nim": "243401009"})
    assert r.status_code == 200
    assert r.json()["status"] == "Ditutup"
    assert r.json()["tindak_lanjut"][0]["ditutup_oleh_pelapor"] is True


def test_ringkasan(klien):
    buat(klien, urgensi="Mendesak")
    buat(klien, ruang="KL 1A")
    c = buat(klien)
    klien.patch(f"/laporan/{c['id']}/status", json={"status": "Selesai"})
    r = klien.get("/ringkasan").json()
    assert r == {
        "total": 3,
        "per_status": {"Menunggu": 2, "Diproses": 0, "Selesai": 1, "Ditutup": 0},
        "per_urgensi": {"Rendah": 0, "Sedang": 2, "Mendesak": 1},
        "terbuka_per_gedung": {"Gedung K": 1, "Gedung V": 1},
        "dibuat_pekan_ini": 3,
    }


def test_laporan_per_ruang(klien):
    a = buat(klien)
    buat(klien, ruang="KL 1A")
    assert [l["id"] for l in klien.get("/ruang/VL 4A/laporan").json()] == [a["id"]]
    r = klien.get("/ruang/ZZ 9/laporan")
    assert r.status_code == 404
    assert r.json()["detail"] == "Ruang ZZ 9 tidak ada"


def test_cors_preflight(klien):
    r = klien.options("/laporan", headers={"Origin": "http://localhost:5000", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "*"


def test_seed(klien):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed.isi(db)
    assert klien.get("/ringkasan").json()["total"] == 12
    assert len(klien.get("/ruang").json()) == 6
