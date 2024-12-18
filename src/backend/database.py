from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///:memory:" if "pytest" in sys.modules else "postgresql://user:pass@localhost:5432/lingualearn"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()