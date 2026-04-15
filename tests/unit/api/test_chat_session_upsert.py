"""Unit tests for ``api.orchestration.session.upsert_session``.

Verifies the create-or-update branching logic without touching
Postgres. The full DB-backed end-to-end test lives in
``tests/integration/test_http_chat.py`` (P8).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.api.orchestration.session import upsert_session
from starry_lyfe.db.models import ChatSession


class _FakeScalar:
    def __init__(self, row: ChatSession | None) -> None:
        self._row = row

    def first(self) -> ChatSession | None:
        return self._row


class _FakeResult:
    def __init__(self, row: ChatSession | None) -> None:
        self._row = row

    def scalars(self) -> _FakeScalar:
        return _FakeScalar(self._row)


class _FakeSession:
    """Tracks ``add()`` + ``flush()`` calls; honors a single seeded row."""

    def __init__(self, existing: ChatSession | None = None) -> None:
        self._existing = existing
        self.added: list[Any] = []
        self.flushed = False

    async def execute(self, *args: object, **kwargs: object) -> _FakeResult:
        return _FakeResult(self._existing)

    def add(self, instance: Any) -> None:
        self.added.append(instance)

    async def flush(self) -> None:
        self.flushed = True


class TestUpsertSessionCreate:
    async def test_creates_new_row_when_absent(self) -> None:
        session = _FakeSession(existing=None)
        sid = uuid.uuid4()
        row = await upsert_session(
            session,  # type: ignore[arg-type]
            session_id=sid,
            client_type="msty",
            character_id="adelia",
            scene_characters=["adelia", "bina"],
        )
        assert row.id == sid
        assert row.client_type == "msty"
        assert row.character_id == "adelia"
        assert row.scene_characters == {"members": ["adelia", "bina"]}
        assert row.turn_count == 1
        assert session.added == [row]
        assert session.flushed is True

    async def test_create_uses_provided_now(self) -> None:
        session = _FakeSession(existing=None)
        moment = datetime(2026, 4, 15, 12, 0, tzinfo=UTC)
        row = await upsert_session(
            session,  # type: ignore[arg-type]
            session_id=uuid.uuid4(),
            client_type="curl",
            character_id="bina",
            now=moment,
        )
        assert row.started_at == moment
        assert row.last_turn_at == moment

    async def test_empty_roster_renders_empty_members_list(self) -> None:
        session = _FakeSession(existing=None)
        row = await upsert_session(
            session,  # type: ignore[arg-type]
            session_id=uuid.uuid4(),
            client_type="msty",
            character_id="reina",
        )
        assert row.scene_characters == {"members": []}


class TestUpsertSessionUpdate:
    async def test_updates_existing_row(self) -> None:
        sid = uuid.uuid4()
        existing = ChatSession(
            id=sid,
            client_type="msty",
            character_id="adelia",
            scene_characters={"members": ["adelia"]},
            started_at=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
            last_turn_at=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
            turn_count=3,
        )
        session = _FakeSession(existing=existing)
        moment = datetime(2026, 4, 15, 11, 30, tzinfo=UTC)
        row = await upsert_session(
            session,  # type: ignore[arg-type]
            session_id=sid,
            client_type="msty",
            character_id="bina",
            scene_characters=["adelia", "bina"],
            now=moment,
        )
        assert row is existing
        assert row.turn_count == 4
        assert row.last_turn_at == moment
        # New focal character carried over.
        assert row.character_id == "bina"
        assert row.scene_characters == {"members": ["adelia", "bina"]}
        # No new row added.
        assert session.added == []
        assert session.flushed is True

    async def test_focal_character_change_recorded(self) -> None:
        sid = uuid.uuid4()
        existing = ChatSession(
            id=sid,
            client_type="msty",
            character_id="adelia",
            scene_characters={"members": ["adelia", "bina"]},
            started_at=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
            last_turn_at=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
            turn_count=1,
        )
        session = _FakeSession(existing=existing)
        await upsert_session(
            session,  # type: ignore[arg-type]
            session_id=sid,
            client_type="msty",
            character_id="reina",
        )
        assert existing.character_id == "reina"


@pytest.fixture
def session_id_for_test() -> uuid.UUID:
    return uuid.uuid4()
