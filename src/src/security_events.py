from src.security_events import router as security_events_router
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "generated_data" / "phantomnet.db"


@router.get("/api/security-events")
def get_security_events(
    limit: int = Query(default=50, ge=1, le=200),
    action: str | None = None
):
    """Return simulated activity records from the local SQLite database."""

    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Activity database not found. Run the Day 9 activity logger first."
        )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        # Confirm that the activities table exists.
        table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'activities'
            """
        ).fetchone()

        if table is None:
            raise HTTPException(
                status_code=503,
                detail="Activities table not found. Run the Day 9 activity logger first."
            )

        # Read the actual table columns so the API can work
        # with the activity logger's existing database schema.
        columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(activities)"
            ).fetchall()
        ]

        query = "SELECT * FROM activities"
        parameters = []

        if action:
            if "action" not in columns:
                raise HTTPException(
                    status_code=400,
                    detail="Action filtering is not supported by this database schema."
                )

            query += " WHERE action = ?"
            parameters.append(action)

        # Newest records first when a timestamp column exists.
        if "timestamp" in columns:
            query += " ORDER BY timestamp DESC"
        elif "created_at" in columns:
            query += " ORDER BY created_at DESC"
        elif "id" in columns:
            query += " ORDER BY id DESC"

        query += " LIMIT ?"
        parameters.append(limit)

        records = connection.execute(
            query, parameters
        ).fetchall()

        return {
            "total": len(records),
            "events": [dict(record) for record in records]
        }

    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {error}"
        )
    finally:
        connection.close()
app.include_router(security_events_router)
