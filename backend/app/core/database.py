"""
Database Session Management — SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLite specific connect args
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_migrations(db_engine):
    """Safely add missing columns to SQLite database without recreating tables or losing data."""
    with db_engine.connect() as conn:
        try:
            # Check existing columns in generated_documents
            result = conn.exec_driver_sql("PRAGMA table_info(generated_documents)")
            existing_cols = {row[1] for row in result.fetchall()}
            if existing_cols:
                cols_to_add = [
                    ("document_id", "VARCHAR(64)"),
                    ("s3_key", "VARCHAR(1024)"),
                    ("content_type", "VARCHAR(100) DEFAULT 'application/json'"),
                    ("file_size_bytes", "INTEGER"),
                    ("status", "VARCHAR(50) DEFAULT 'completed'"),
                    ("meta", "JSON"),
                ]
                for col_name, col_type in cols_to_add:
                    if col_name not in existing_cols:
                        conn.exec_driver_sql(f"ALTER TABLE generated_documents ADD COLUMN {col_name} {col_type}")
                conn.commit()
        except Exception as e:
            # Table might not exist yet, Base.metadata.create_all will create it
            pass


def get_db():
    """Dependency: yields a database session and ensures it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

