from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    from fastapi import Depends
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lightweight migration helper for SQLite
def ensure_column(engine, table_name: str, column_name: str, column_type_sql: str):
    with engine.connect() as conn:
        # SQLAlchemy 2.0: use exec_driver_sql for driver-level SQL
        res = conn.exec_driver_sql(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in res.fetchall()]
        if column_name not in existing_cols:
            conn.exec_driver_sql(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type_sql}"
            )