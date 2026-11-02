
import argparse
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "generated_data"
DB_PATH = DATA_DIR / "phantomnet.db"


def get_timestamp():
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_database():
    """Connect to the local PhantomNet database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_activity_tables(connection):
    """Create session and activity tables."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            start_time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            command TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            event_time TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (session_id)
                REFERENCES sessions(session_id)
        )
    """)

    connection.commit()


def create_session(connection, username):
    """Create a fictional simulation session."""

    session_id = "SES-" + uuid.uuid4().hex[:8].upper()

    connection.execute("""
        INSERT INTO sessions
        (session_id, username, start_time, status)
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        username,
        get_timestamp(),
        "ACTIVE"
    ))

    connection.commit()

    print(f"Session created: {session_id}")
    return session_id


def log_activity(connection, session_id, command, activity_type, details):
    """Record a simulated command activity."""

    cursor = connection.execute("""
        SELECT session_id
        FROM sessions
        WHERE session_id = ? AND status = 'ACTIVE'
    """, (session_id,))

    if cursor.fetchone() is None:
        raise ValueError("Active session not found.")

    connection.execute("""
        INSERT INTO activities
        (session_id, command, activity_type, event_time, details)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_id,
        command,
        activity_type,
        get_timestamp(),
        details
    ))

    connection.commit()

    print(f"Activity logged: {command}")


def close_session(connection, session_id):
    """Mark a session as completed."""

    cursor = connection.execute("""
        UPDATE sessions
        SET status = 'CLOSED'
        WHERE session_id = ? AND status = 'ACTIVE'
    """, (session_id,))

    connection.commit()

    if cursor.rowcount == 0:
        raise ValueError("Active session not found.")

    print("Session closed successfully.")


def show_activities(connection):
    """Display all recorded simulation activities."""

    cursor = connection.execute("""
        SELECT
            activity_id,
            session_id,
            command,
            activity_type,
            event_time,
            details
        FROM activities
        ORDER BY activity_id
    """)

    records = cursor.fetchall()

    print("\n--- PhantomNet Activity Log ---")

    if not records:
        print("No activities recorded yet.")
        return

    for record in records:
        print("-" * 55)
        print(f"Activity ID : {record[0]}")
        print(f"Session ID  : {record[1]}")
        print(f"Command     : {record[2]}")
        print(f"Type        : {record[3]}")
        print(f"Time        : {record[4]}")
        print(f"Details     : {record[5]}")


def show_sessions(connection):
    """Display all simulation sessions."""

    cursor = connection.execute("""
        SELECT session_id, username, start_time, status
        FROM sessions
        ORDER BY start_time DESC
    """)

    records = cursor.fetchall()

    print("\n--- PhantomNet Sessions ---")

    if not records:
        print("No sessions found.")
        return

    for record in records:
        print("-" * 45)
        print(f"Session ID : {record[0]}")
        print(f"Username   : {record[1]}")
        print(f"Start Time : {record[2]}")
        print(f"Status     : {record[3]}")


def run_demo(connection):
    """Create a fictional session and log sample commands."""

    username = "demo_employee"
    session_id = create_session(connection, username)

    sample_activities = [
        (
            "LIST_DOCUMENTS",
            "FILE_ACCESS",
            "Listed fictional corporate documents"
        ),
        (
            "VIEW_REPORT",
            "DOCUMENT_ACCESS",
            "Viewed a synthetic department report"
        ),
        (
            "SEARCH_EMPLOYEE",
            "DATABASE_QUERY",
            "Searched the fictional employee database"
        ),
        (
            "VIEW_PROJECT",
            "PROJECT_ACCESS",
            "Viewed fictional project information"
        )
    ]

    for command, activity_type, details in sample_activities:
        log_activity(
            connection,
            session_id,
            command,
            activity_type,
            details
        )

    close_session(connection, session_id)

    print("\nDemo activity completed.")


def main():
    parser = argparse.ArgumentParser(
        description="PhantomNet session and activity logger"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Create a sample fictional session and activities"
    )

    parser.add_argument(
        "--show",
        choices=["sessions", "activities"],
        help="Display stored sessions or activities"
    )

    args = parser.parse_args()

    try:
        with connect_database() as connection:
            create_activity_tables(connection)

            if args.demo:
                run_demo(connection)

            elif args.show == "sessions":
                show_sessions(connection)

            else:
                show_activities(connection)

    except (sqlite3.Error, ValueError, OSError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
