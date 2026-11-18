import os
import tempfile
from pathlib import Path

# Harus sebelum import app: load_dotenv tidak menimpa variabel yang sudah ada, jadi tes tidak menyentuh Neon.
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'tes.db'}"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Ruang


@pytest.fixture(autouse=True)
def klien():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add_all([
            Ruang(kode="VL 4A", gedung="Gedung V", jadwal_pakai="Senin 08.00-09.40", status_kelayakan="layak"),
            Ruang(kode="KL 1A", gedung="Gedung K", jadwal_pakai="Selasa 10.00-11.40", status_kelayakan="layak"),
        ])
        db.commit()
    with TestClient(app) as k:
        yield k


def buat(klien, **ubah):
    body = {
        "ruang": "VL 4A",
        "judul": "Proyektor mati",
        "deskripsi": "Tidak menyala sejak pagi.",
        "nim_pelapor": "243401009",
        **ubah,
    }
    r = klien.post("/laporan", json=body)
    assert r.status_code == 201, r.text
    return r.json()
