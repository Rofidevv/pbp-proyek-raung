from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, sekarang
from .models import Laporan, Ruang, Status, TindakLanjut, Urgensi, Urut
from .schemas import (
    LaporanBaru,
    LaporanDetail,
    LaporanKeluar,
    LaporanUbah,
    NimMasuk,
    Ringkasan,
    RuangKeluar,
    StatusUbah,
    TindakLanjutBaru,
    TindakLanjutKeluar,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="LaporFas API", lifespan=lifespan)
# Origin bebas aman karena tidak ada login dan cookie; allow_credentials tetap False.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = Annotated[Session, Depends(get_db)]


def cari_laporan(db: Session, id: int) -> Laporan:
    lap = db.get(Laporan, id)
    if lap is None:
        raise HTTPException(404, f"Laporan {id} tidak ada")
    return lap


def pastikan_ruang(db: Session, kode: str) -> None:
    if db.get(Ruang, kode) is None:
        raise HTTPException(422, f"Ruang {kode} tidak ada")


def pastikan_menunggu(lap: Laporan) -> None:
    if lap.status != Status.MENUNGGU:
        raise HTTPException(409, "Laporan hanya bisa diubah atau dihapus selama statusnya Menunggu")


@app.get("/ruang", response_model=list[RuangKeluar])
def daftar_ruang(db: DB):
    return db.scalars(select(Ruang).order_by(Ruang.kode)).all()


@app.get("/ruang/{kode}/laporan", response_model=list[LaporanKeluar])
def laporan_ruang(kode: str, db: DB):
    if db.get(Ruang, kode) is None:
        raise HTTPException(404, f"Ruang {kode} tidak ada")
    return db.scalars(
        select(Laporan).where(Laporan.ruang == kode).order_by(Laporan.dibuat_pada.desc(), Laporan.id.desc())
    ).all()


@app.get("/laporan", response_model=list[LaporanKeluar])
def daftar_laporan(
    db: DB,
    status: Status | None = None,
    urgensi: Urgensi | None = None,
    ruang: str | None = None,
    q: str | None = None,
    urut: Urut = Urut.TERBARU,
):
    kueri = select(Laporan)
    if status:
        kueri = kueri.where(Laporan.status == status)
    if urgensi:
        kueri = kueri.where(Laporan.urgensi == urgensi)
    if ruang:
        kueri = kueri.where(Laporan.ruang == ruang)
    if q:
        kueri = kueri.where(or_(Laporan.judul.ilike(f"%{q}%"), Laporan.deskripsi.ilike(f"%{q}%")))
    if urut == Urut.TERLAMA:
        return db.scalars(kueri.order_by(Laporan.dibuat_pada, Laporan.id)).all()
    hasil = db.scalars(kueri.order_by(Laporan.dibuat_pada.desc(), Laporan.id.desc())).all()
    if urut == Urut.PRIORITAS:
        # shortcut: urut prioritas di Python karena dukungan ada di kolom JSON; pindah ke SQL bila laporan ribuan
        tingkat = list(Urgensi)
        hasil = sorted(hasil, key=lambda l: (-tingkat.index(l.urgensi), -l.dukungan, l.dibuat_pada))
    return hasil


@app.post("/laporan", response_model=LaporanDetail, status_code=201)
def buat_laporan(body: LaporanBaru, db: DB):
    pastikan_ruang(db, body.ruang)
    lap = Laporan(**body.model_dump(), status=Status.MENUNGGU, pendukung=[body.nim_pelapor])
    db.add(lap)
    db.commit()
    return lap


@app.get("/laporan/{id}", response_model=LaporanDetail)
def detail_laporan(id: int, db: DB):
    return cari_laporan(db, id)


@app.put("/laporan/{id}", response_model=LaporanDetail)
def ubah_laporan(id: int, body: LaporanUbah, db: DB):
    lap = cari_laporan(db, id)
    pastikan_menunggu(lap)
    pastikan_ruang(db, body.ruang)
    for kolom, nilai in body.model_dump().items():
        setattr(lap, kolom, nilai)
    db.commit()
    return lap


@app.patch("/laporan/{id}/status", response_model=LaporanDetail)
def ubah_status(id: int, body: StatusUbah, db: DB):
    lap = cari_laporan(db, id)
    lap.status = body.status
    if body.urgensi is not None:
        lap.urgensi = body.urgensi
    db.commit()
    return lap


@app.delete("/laporan/{id}", response_model=LaporanKeluar)
def hapus_laporan(id: int, db: DB):
    lap = cari_laporan(db, id)
    pastikan_menunggu(lap)
    hasil = LaporanKeluar.model_validate(lap)
    db.delete(lap)
    db.commit()
    return hasil


@app.post("/laporan/{id}/dukungan", response_model=LaporanKeluar, status_code=201)
def dukung_laporan(id: int, body: NimMasuk, db: DB):
    lap = cari_laporan(db, id)
    if body.nim in lap.pendukung:
        raise HTTPException(409, f"NIM {body.nim} sudah mendukung laporan ini")
    # List baru, bukan append: SQLAlchemy tidak melacak perubahan di dalam kolom JSON.
    lap.pendukung = [*lap.pendukung, body.nim]
    db.commit()
    return lap


@app.get("/laporan/{id}/tindak-lanjut", response_model=list[TindakLanjutKeluar])
def daftar_tindak_lanjut(id: int, db: DB):
    return cari_laporan(db, id).tindak_lanjut


@app.post("/laporan/{id}/tindak-lanjut", response_model=TindakLanjutKeluar, status_code=201)
def buat_tindak_lanjut(id: int, body: TindakLanjutBaru, db: DB):
    lap = cari_laporan(db, id)
    tl = TindakLanjut(laporan=lap, catatan_sarpras=body.catatan_sarpras)
    db.add(tl)
    db.commit()
    return tl


@app.post("/laporan/{id}/tutup", response_model=LaporanDetail)
def tutup_laporan(id: int, body: NimMasuk, db: DB):
    lap = cari_laporan(db, id)
    if body.nim != lap.nim_pelapor:
        raise HTTPException(403, "Hanya pelapor yang bisa menutup laporan ini")
    if lap.status != Status.SELESAI:
        raise HTTPException(409, "Laporan baru bisa ditutup sesudah statusnya Selesai")
    lap.status = Status.DITUTUP
    db.add(TindakLanjut(
        laporan=lap,
        catatan_sarpras="Ditutup oleh pelapor sesudah memeriksa hasil perbaikan",
        ditutup_oleh_pelapor=True,
    ))
    db.commit()
    db.refresh(lap)
    return lap


@app.get("/ringkasan", response_model=Ringkasan)
def ringkasan(db: DB):
    baris = db.execute(
        select(Laporan.status, Laporan.urgensi, Laporan.dibuat_pada, Ruang.gedung).join(Ruang, Laporan.ruang == Ruang.kode)
    ).all()
    kini = sekarang()
    senin = (kini - timedelta(days=kini.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    per_status = {s.value: 0 for s in Status}
    per_urgensi = {u.value: 0 for u in Urgensi}
    terbuka = {g: 0 for g in db.scalars(select(Ruang.gedung).distinct().order_by(Ruang.gedung))}
    pekan_ini = 0
    for status, urgensi, dibuat_pada, gedung in baris:
        per_status[status] += 1
        per_urgensi[urgensi] += 1
        if status in (Status.MENUNGGU, Status.DIPROSES):
            terbuka[gedung] += 1
        pekan_ini += dibuat_pada >= senin
    return Ringkasan(
        total=len(baris),
        per_status=per_status,
        per_urgensi=per_urgensi,
        terbuka_per_gedung=terbuka,
        dibuat_pekan_ini=pekan_ini,
    )
