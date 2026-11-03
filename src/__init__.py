
import sqlite3
import pytest

from src import (
    file_generator,
    content_generator,
    employee_database,
    activity_logger,
    prompt_engine,
)


# Sample fictional company data for testing
TEST_LORE = {
    "company": {
        "name": "Nexora Technologies",
        "industry": "Technology",
        "headquarters": "Austin"
    },
    "security_context": {
        "environment": "Test simulation",
        "data_classification": "Synthetic"
    },
    "executives": [
        {
            "id": "EMP001",
            "name": "Olivia Carter",
            "role": "CEO"
        }
    ],
    "departments": [
        "Engineering",
        "Finance"
    ],
    "technology_stack": ["Python", "SQLite"],
    "fictional_projects": [
        {
            "name": "Project Northstar",
            "description": "Cloud monitoring project",
            "owner": "Olivia Carter",
            "status": "In Progress"
        }
    ],
    "corporate_vocabulary": [
        "quarterly review",
        "security audit"
    ],
    "file_generation": {
        "default_directories": ["Engineering", "Finance"],
        "default_file_extensions": [".txt", ".md"]
    }
}


# Test 1: Filename generator
def test_filename_generator():
    first = file_generator.generate_filenames(
        TEST_LORE, count=5, seed=42
    )
    second = file_generator.generate_filenames(
        TEST_LORE, count=5, seed=42
    )

    assert len(first) == 5
    assert first == second


# Test 2: Content generator
def test_content_generator():
    first = content_generator.generate_documents(
        TEST_LORE, count=2, seed=42
    )

    assert len(first) == 2

    for department, filename, content in first:
        assert department in TEST_LORE["departments"]
        assert filename.endswith(".md")
        assert len(content) > 0


# Test 3: Employee database
def test_employee_database():
    connection = sqlite3.connect(":memory:")

    try:
        employee_database.create_database(connection)

        employee_database.insert_employee(
            connection,
            "EMP_TEST",
            "Test Employee",
            "Developer",
            "Engineering",
            "Project Northstar"
        )

        result = connection.execute(
            "SELECT name FROM employees WHERE employee_id = ?",
            ("EMP_TEST",)
        ).fetchone()

        assert result is not None
        assert result[0] == "Test Employee"

    finally:
        connection.close()


# Test 4: Activity logger
def test_activity_logger():
    connection = sqlite3.connect(":memory:")

    try:
        activity_logger.create_activity_tables(connection)

        session_id = activity_logger.create_session(
            connection, "test_employee"
        )

        activity_logger.log_activity(
            connection,
            session_id,
            "LIST_DOCUMENTS",
            "Listed fictional documents"
        )

        result = connection.execute(
            "SELECT action FROM activities WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        assert result is not None
        assert result[0] == "LIST_DOCUMENTS"

        activity_logger.close_session(connection, session_id)

        with pytest.raises(ValueError):
            activity_logger.log_activity(
                connection,
                session_id,
                "VIEW_REPORT",
                "Attempt after session closed"
            )

    finally:
        connection.close()


# Test 5: Prompt engine
def test_prompt_engine():
    prompt = prompt_engine.build_prompt(
        TEST_LORE,
        department="Engineering",
        document_type="Deployment Report"
    )

    assert "Nexora Technologies" in prompt
    assert "Engineering" in prompt
    assert "Deployment Report" in prompt
