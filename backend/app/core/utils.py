from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a naive UTC datetime (no tzinfo).

    PostgreSQL TIMESTAMP WITHOUT TIME ZONE requires naive datetimes.
    Never use datetime.now(timezone.utc) directly in model defaults.
    """
    return datetime.now(UTC).replace(tzinfo=None)
