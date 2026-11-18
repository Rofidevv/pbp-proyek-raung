from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, sekarang


class Status(StrEnum):
    MENUNGGU = "Menunggu"
    DIPROSES = "Diproses"
    SELESAI = "Selesai"
    DITUTUP = "Ditutup"


# Urutan deklarasi rendah ke mendesak dipakai untuk urut prioritas.
class Urgensi(StrEnum):
    RENDAH = "Rendah"
    SEDANG = "Sedang"
    MENDESAK = "Mendesak"


class Kelayakan(StrEnum):
    LAYAK = "layak"
    ADA_LAPORAN_TERBUKA = "ada_laporan_terbuka"
    TIDAK_LAYAK = "tidak_layak"


class Urut(StrEnum):
    TERBARU = "terbaru"
    TERLAMA = "terlama"
    PRIORITAS = "prioritas"


class Ruang(Base):
    __tablename__ = "ruang"

    kode: Mapped[str] = mapped_column(String(20), primary_key=True)
    gedung: Mapped[str] = mapped_column(String(60))
    jadwal_pakai: Mapped[str] = mapped_column(String(200))
    status_kelayakan: Mapped[str] = mapped_column(String(20))
    dibuat_pada: Mapped[datetime] = mapped_column(default=sekarang)


class Laporan(Base):
    __tablename__ = "laporan"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ruang: Mapped[str] = mapped_column(ForeignKey("ruang.kode"))
    judul: Mapped[str] = mapped_column(String(120))
    deskripsi: Mapped[str] = mapped_column(Text)
    foto_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default=Status.MENUNGGU)
    urgensi: Mapped[str] = mapped_column(String(20))
    nim_pelapor: Mapped[str] = mapped_column(String(9))
    # Daftar NIM pendukung; respons API hanya memuat jumlahnya.
    pendukung: Mapped[list[str]] = mapped_column(JSON, default=list)
    dibuat_pada: Mapped[datetime] = mapped_column(default=sekarang)
    diubah_pada: Mapped[datetime] = mapped_column(default=sekarang, onupdate=sekarang)

    tindak_lanjut: Mapped[list["TindakLanjut"]] = relationship(
        back_populates="laporan",
        cascade="all, delete-orphan",
        order_by=lambda: (TindakLanjut.dibuat_pada.desc(), TindakLanjut.id.desc()),
    )

    @property
    def dukungan(self) -> int:
        return len(self.pendukung)


class TindakLanjut(Base):
    __tablename__ = "tindak_lanjut"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    laporan_id: Mapped[int] = mapped_column(ForeignKey("laporan.id"))
    catatan_sarpras: Mapped[str] = mapped_column(Text)
    ditutup_oleh_pelapor: Mapped[bool] = mapped_column(default=False)
    dibuat_pada: Mapped[datetime] = mapped_column(default=sekarang)

    laporan: Mapped[Laporan] = relationship(back_populates="tindak_lanjut")
