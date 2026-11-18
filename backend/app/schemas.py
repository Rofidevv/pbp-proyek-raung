from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from .models import Kelayakan, Status, Urgensi

Teks = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Nim = Annotated[str, StringConstraints(pattern=r"^\d{9}$")]


class LaporanUbah(BaseModel):
    ruang: Teks
    judul: Annotated[Teks, StringConstraints(max_length=120)]
    deskripsi: Teks
    foto_url: str | None = None
    urgensi: Urgensi = Urgensi.SEDANG


class LaporanBaru(LaporanUbah):
    nim_pelapor: Nim


class StatusUbah(BaseModel):
    status: Status
    urgensi: Urgensi | None = None


class NimMasuk(BaseModel):
    nim: Nim


class TindakLanjutBaru(BaseModel):
    catatan_sarpras: Teks


class Keluar(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RuangKeluar(Keluar):
    kode: str
    gedung: str
    jadwal_pakai: str
    status_kelayakan: Kelayakan
    dibuat_pada: datetime


class TindakLanjutKeluar(Keluar):
    id: int
    laporan_id: int
    catatan_sarpras: str
    ditutup_oleh_pelapor: bool
    dibuat_pada: datetime


class LaporanKeluar(Keluar):
    id: int
    ruang: str
    judul: str
    deskripsi: str
    foto_url: str | None
    status: Status
    urgensi: Urgensi
    nim_pelapor: str
    dukungan: int
    dibuat_pada: datetime
    diubah_pada: datetime


class LaporanDetail(LaporanKeluar):
    tindak_lanjut: list[TindakLanjutKeluar]


class Ringkasan(BaseModel):
    total: int
    per_status: dict[str, int]
    per_urgensi: dict[str, int]
    terbuka_per_gedung: dict[str, int]
    dibuat_pekan_ini: int
