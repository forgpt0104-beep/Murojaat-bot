#!/bin/sh
set -e

echo "Waiting for PostgreSQL to become available..."
python - <<'PYEOF'
import asyncio
import sys
import time

from sqlalchemy.ext.asyncio import create_async_engine

from bot.config import settings


async def wait_for_db(max_attempts: int = 30, delay: float = 2.0) -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            await engine.dispose()
            print("Database is ready.")
            return
        except Exception as exc:
            print(f"[{attempt}/{max_attempts}] Database not ready yet: {exc}")
            time.sleep(delay)
    print("Database never became available.", file=sys.stderr)
    sys.exit(1)


asyncio.run(wait_for_db())
PYEOF

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting bot..."
exec "$@"
