import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
URL = os.getenv("DATABASE_URL", "sqlite:///./laporfas.db")

# pool_pre_ping: Neon menidurkan database saat sepi dan memutus koneksi lama.
engine = create_engine(
    URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Offset tetap, bukan zoneinfo: Windows tidak punya tz database tanpa paket tzdata.
WIB = timezone(timedelta(hours=7))


def sekarang() -> datetime:
    return datetime.now(WIB).replace(tzinfo=None)


def get_db():
    with SessionLocal() as db:
        yield db
