
import argparse
import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LORE_PATH = PROJECT_ROOT / "config" / "company_lore.json"
DB_DIR = PROJECT_ROOT / "generated_data"
DB_PATH = DB_DIR / "phantomnet.db"


# Entirely fictional sample employees
SAMPLE_EMPLOYEES = [
    {
        "id": "EMP005",
        "name": "Ava Wilson",
        "role": "Software Engineer",
        "department": "Engineering",
        "project": "Project Northstar"
    },
    {
        "id": "EMP006",
        "name": "Liam Foster",
        "role": "Financial Analyst",
        "department": "Finance",
        "project": "Project Lighthouse"
    },
    {
        "id": "EMP007",
        "name": "Mia Turner",
        "role": "HR Coordinator",
        "department": "HumanResources",
        "project": "Project Northstar"
    },
    {
        "id": "EMP008",
        "name": "Lucas Reed",
        "role": "Security Analyst",
        "department": "Security",
        "project": "Project Lighthouse"
    },
    {
        "id": "EMP009",
        "name": "Isabella Clark",
        "role": "IT Support Engineer",
        "department": "IT",
        "project": "Project Northstar"
    },
    {
        "id": "EMP010",
        "name": "James Parker",
        "role": "Cloud Engineer",
        "department": "Cloud Infrastructure",
        "project": "Project Lighthouse"
    }
]


def load_lore():
    """Load fictional company information."""
    if not LORE_PATH.exists():
        raise FileNotFoundError("company_lore.json was not found.")

    with LORE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_database(connection):
    """Create employee and project tables."""

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            project TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_name TEXT PRIMARY KEY,
            description TEXT,
            owner TEXT,
            status TEXT
        )
    """)

    connection.commit()


def insert_employee(connection, employee):
    """Insert or update a fictional employee record."""

    connection.execute("""
        INSERT OR REPLACE INTO employees
        (employee_id, name, role, department, project)
        VALUES (?, ?, ?, ?, ?)
    """, (
        employee["id"],
        employee["name"],
        employee["role"],
        employee["department"],
        employee["project"]
    ))

    connection.commit()


def insert_project(connection, project):
    """Insert or update a fictional project."""

    connection.execute("""
        INSERT OR REPLACE INTO projects
        (project_name, description, owner, status)
        VALUES (?, ?, ?, ?)
    """, (
        project.get("name", "Sample Project"),
        project.get("description", ""),
        project.get("owner", "Sample Employee"),
        project.get("status", "Planning")
    ))

    connection.commit()


def load_initial_data(connection, lore):
    """Load fictional executives, employees and projects."""

    for executive in lore.get("executives", []):
        employee = {
            "id": executive["id"],
            "name": executive["name"],
            "role": executive["role"],
            "department": "Management",
            "project": "Project Northstar"
        }
        insert_employee(connection, employee)

    for employee in SAMPLE_EMPLOYEES:
        insert_employee(connection, employee)

    for project in lore.get("fictional_projects", []):
        insert_project(connection, project)


def display_employees(connection):
    """Display all fictional employee records."""

    cursor = connection.execute("""
        SELECT employee_id, name, role, department, project
        FROM employees
        ORDER BY employee_id
    """)

    records = cursor.fetchall()

    print("\n--- PhantomNet Employee Records ---")

    if not records:
        print("No employee records found.")
        return

    for record in records:
        print("-" * 45)
        print(f"Employee ID : {record[0]}")
        print(f"Name        : {record[1]}")
        print(f"Role        : {record[2]}")
        print(f"Department  : {record[3]}")
        print(f"Project     : {record[4]}")


def display_projects(connection):
    """Display fictional company projects."""

    cursor = connection.execute("""
        SELECT project_name, description, owner, status
        FROM projects
        ORDER BY project_name
    """)

    records = cursor.fetchall()

    print("\n--- PhantomNet Project Records ---")

    for record in records:
        print("-" * 45)
        print(f"Project     : {record[0]}")
        print(f"Description : {record[1]}")
        print(f"Owner       : {record[2]}")
        print(f"Status      : {record[3]}")


def search_employee(connection, employee_id):
    """Search for an employee using an employee ID."""

    cursor = connection.execute("""
        SELECT employee_id, name, role, department, project
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    record = cursor.fetchone()

    if record:
        print("\nEmployee Found:")
        print(f"ID         : {record[0]}")
        print(f"Name       : {record[1]}")
        print(f"Role       : {record[2]}")
        print(f"Department : {record[3]}")
        print(f"Project    : {record[4]}")
    else:
        print("Employee not found.")


def main():
    parser = argparse.ArgumentParser(
        description="PhantomNet synthetic corporate database"
    )

    parser.add_argument(
        "--show",
        choices=["employees", "projects"],
        help="Display employee or project records"
    )

    parser.add_argument(
        "--search",
        help="Search an employee using an ID, such as EMP005"
    )

    args = parser.parse_args()

    try:
        lore = load_lore()
        DB_DIR.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(DB_PATH) as connection:
            create_database(connection)
            load_initial_data(connection, lore)

            print(f"Database: {DB_PATH}")

            if args.search:
                search_employee(connection, args.search)

            elif args.show == "projects":
                display_projects(connection)

            else:
                display_employees(connection)

        print("\nSynthetic database operation completed.")

    except (FileNotFoundError, json.JSONDecodeError, KeyError,
            sqlite3.Error, OSError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
