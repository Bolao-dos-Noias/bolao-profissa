import os
import tempfile

import httpx
import pytest
import pytest_asyncio
from sqlmodel import SQLModel

tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db.name}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["APP_ENV"] = "test"
os.environ["ADMIN_PASSWORD"] = "admin-test"
os.environ["BOLAO_DEADLINE_UTC"] = "2030-01-01T00:00:00Z"

from app import db as app_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    SQLModel.metadata.drop_all(app_db.engine)
    SQLModel.metadata.create_all(app_db.engine)
    app_db.init_db()
    try:
        from app.security import limiter

        limiter.reset()
    except Exception:
        pass
    yield


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
