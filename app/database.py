from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)


DATABASE_URL = "sqlite:///./protective_intelligence.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def ensure_case_archive_columns() -> None:
    """
    Add case-archiving columns to an existing SQLite database.

    SQLAlchemy's create_all() creates missing tables, but it does
    not add new columns to tables that already exist. This
    compatibility migration preserves the current database and
    adds only the missing columns.
    """
    with engine.begin() as connection:
        inspector = inspect(connection)

        if "cases" not in inspector.get_table_names():
            return

        existing_columns = {
            column["name"]
            for column in inspector.get_columns("cases")
        }

        if "is_archived" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN is_archived BOOLEAN "
                    "NOT NULL DEFAULT 0"
                )
            )

        if "archived_at" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN archived_at DATETIME"
                )
            )

        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_cases_is_archived "
                "ON cases (is_archived)"
            )
        )


def ensure_case_assignment_columns() -> None:
    """
    Add case-assignment columns to an existing SQLite database.

    This compatibility migration preserves existing case records
    and adds only the assignment fields that are missing from the
    cases table.
    """
    with engine.begin() as connection:
        inspector = inspect(connection)

        if "cases" not in inspector.get_table_names():
            return

        existing_columns = {
            column["name"]
            for column in inspector.get_columns("cases")
        }

        if "assigned_analyst" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN assigned_analyst VARCHAR(150)"
                )
            )

        if "responsible_team" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN responsible_team VARCHAR(150)"
                )
            )

        if "assigned_at" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN assigned_at DATETIME"
                )
            )

        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_cases_assigned_analyst "
                "ON cases (assigned_analyst)"
            )
        )

        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_cases_responsible_team "
                "ON cases (responsible_team)"
            )
        )


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()