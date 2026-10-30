from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from minidash.app import create_app

# Monday 2026-11-02, 12:00 UTC: Bella Napoli (11:00-22:00) is open.
T0 = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)


class FixedClock:
    """A clock that only moves when a test moves it."""

    def __init__(self, now: datetime):
        self.current = now

    def now(self) -> datetime:
        return self.current


@pytest.fixture
def clock():
    return FixedClock(T0)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def client(db_path, clock):
    with TestClient(create_app(db_path, clock=clock)) as c:
        yield c
