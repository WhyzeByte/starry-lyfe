"""SQLAlchemy declarative base and schema configuration."""

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase

SCHEMA: str = "starry_lyfe"

# Shared timezone-aware timestamp type for all ORM models.
TZDateTime = DateTime(timezone=True)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all ORM models. All tables live in the starry_lyfe schema."""

    metadata = MetaData(schema=SCHEMA, naming_convention=convention)
