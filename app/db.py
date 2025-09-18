from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
import os
from pathlib import Path


# Database configuration with environment variable support
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "finnews")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if DB_TYPE == "sqlite":
    # For SQLite, use local file path
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, f"{DB_NAME}.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
elif DB_TYPE == "postgresql":
    # For PostgreSQL
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif DB_TYPE == "mysql":
    # For MySQL
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Default to SQLite
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, f"{DB_NAME}.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    pass


# Create engine with appropriate configuration
if DB_TYPE == "sqlite":
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DB_ECHO", "false").lower() == "true"
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
    )


SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


