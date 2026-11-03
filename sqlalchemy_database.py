from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from config import settings

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.user,
    password=settings.password,
    host=settings.host,
    port=settings.port,
    database=settings.name
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()