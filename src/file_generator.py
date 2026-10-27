
import argparse
import json
import random
import re
from pathlib import Path


# Locate the project root from this file:
# project_root/src/file_generator.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LORE_PATH = PROJECT_ROOT / "config" / "company_lore.json"

FILE_TEMPLATES = {
    "Finance": [
        "quarterly_budget",
        "expense_summary",
        "invoice_register",
        "financial_forecast",
    ],
    "Engineering": [
        "deployment_notes",
        "service_reliability",
        "release_checklist",
        "system_architecture",
    ],
    "HumanResources": [
        "employee_directory",
        "onboarding_checklist",
        "training_schedule",
        "team_roster",
    ],
    "IT": [
        "asset_inventory",
        "maintenance_schedule",
        "support_summary",
        "system_health_report",
    ],
    "Security": [
        "access_audit",
        "incident_summary",
        "security_review",
        "monitoring_report",
    ],
    "Projects": [
        "project_status",
        "meeting_notes",
        "milestone_tracker",
        "progress_report",
    ],
}

EXTENSIONS = [".txt", ".csv", ".json", ".md", ".log"]


def load_company_lore():
    """Load and validate the fictional company configuration."""
    if not LORE_PATH.exists():
        raise FileNotFoundError(
            f"Company lore file not found: {LORE_PATH}"
        )

    with LORE_PATH.open("r", encoding="utf-8") as file:
        lore = json.load(file)

    company = lore.get("company", {})
    if not company.get("name"):
        raise ValueError("Company name is missing from company_lore.json")

    directories = lore.get("file_generation", {}).get(
        "default_directories", []
    )
    if not directories:
        raise ValueError("No default directories configured in company lore")

    return lore


def safe_filename(value):
    """Convert a label into a safe filename component."""
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value.strip("_") or "document"


def generate_filenames(lore, count=10, seed=None):
    """Generate unique, fictional corporate filenames."""
    if count < 1:
        raise ValueError("Count must be at least 1")

    rng = random.Random(seed)
    directories = lore["file_generation"]["default_directories"]

    configured_extensions = lore["file_generation"].get(
        "default_file_extensions", EXTENSIONS
    )
    extensions = [
        ext if ext.startswith(".") else f".{ext}"
        for ext in configured_extensions
        if ext
    ]

    if not extensions:
        extensions = EXTENSIONS

    company_name = safe_filename(lore["company"]["name"])
    filenames = set()

    while len(filenames) < count:
        directory = rng.choice(directories)
        templates = FILE_TEMPLATES.get(
            directory,
            ["general_notes", "status_report", "work_summary"],
        )
        document = rng.choice(templates)
        year = rng.choice([2024, 2025, 2026])
        month = rng.randint(1, 12)
        extension = rng.choice(extensions)

        filename = (
            f"{company_name}_{document}_{year}_"
            f"{month:02d}{extension}"
        )

        filenames.add((directory, filename))

    return sorted(filenames)


def main():
    parser = argparse.ArgumentParser(
        description="Generate fictional corporate filenames for PhantomNet."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of filenames to generate (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for repeatable output",
    )
    args = parser.parse_args()

    try:
        lore = load_company_lore()
        results = generate_filenames(
            lore,
            count=args.count,
            seed=args.seed,
        )

        print(f"Company: {lore['company']['name']}")
        print(f"Generated {len(results)} fictional filenames:\n")

        for directory, filename in results:
            print(f"{directory}/{filename}")

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
