"""Configuration de la base de données SQLite (SQLAlchemy)."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Chemin configurable via variable d'environnement (utile en Docker / Render)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stages.db")

engine = create_engine(
    DATABASE_URL,
    # Nécessaire pour SQLite : FastAPI peut utiliser plusieurs threads
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dépendance FastAPI : ouvre une session par requête puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
