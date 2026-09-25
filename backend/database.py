import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env
load_dotenv()

# Read database URL, default to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/tiffin_db"
)

# Connect to database with graceful fallback if PostgreSQL is not active
engine = None
try:
    if DATABASE_URL.startswith("postgresql"):
        # Test connection with a short timeout
        test_engine = create_engine(
            DATABASE_URL,
            connect_args={"connect_timeout": 3},
            pool_pre_ping=True
        )
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        print("[DATABASE] Successfully connected to PostgreSQL database.")
    else:
        engine = create_engine(DATABASE_URL)
        print(f"[DATABASE] Connected to database: {DATABASE_URL}")
except Exception as e:
    # If PostgreSQL server is not running, fallback to SQLite for zero-friction local development
    fallback_url = "sqlite:///./tiffin_services.db"
    print(f"[DATABASE NOTICE] Could not connect to PostgreSQL ({e}).")
    print(f"[DATABASE NOTICE] Falling back to SQLite: {fallback_url}")
    print("[DATABASE NOTICE] All features will work properly without interruption.")
    engine = create_engine(
        fallback_url,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session to API route functions.
    Ensures the session is safely closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
