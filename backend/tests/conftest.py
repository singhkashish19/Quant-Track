import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{BACKEND_ROOT / 'quanttrack_test.db'}",
)

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
