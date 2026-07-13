import os
import tempfile
from pathlib import Path

import pytest


_db_path = Path(tempfile.gettempdir()) / "ai_first_crm_hcp_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["LOG_LEVEL"] = "WARNING"

import app.models  # noqa: E402,F401
from app.database.base import Base  # noqa: E402
from app.database.session import engine  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

