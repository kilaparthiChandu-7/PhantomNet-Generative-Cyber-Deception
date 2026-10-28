
import argparse
import json
import random
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LORE_PATH = PROJECT_ROOT / "config" / "company_lore.json"
OUTPUT_DIR = PROJECT_ROOT / "generated_docs"

DOCUMENT_TEMPLATES = {
    "Finance": [
        ("Quarterly Budget Summary",
         "This fictional report summarizes planned departmental spending."),
        ("Expense Review",
         "This fictional review groups routine operating expenses."),
        ("Financial Forecast",
         "This fictional forecast outlines estimated costs for the next quarter.")
    ],
    "Engineering": [
        ("Deployment Notes",
         "This fictional document records a simulated software deployment."),
        ("Service Reliability Report",
         "This fictional report reviews simulated service reliability."),
        ("Release Checklist",
         "This fictional checklist tracks routine release preparation.")
    ],
    "HumanResources": [
        ("Onboarding Checklist",
         "This fictional checklist summarizes a new employee's onboarding tasks."),
        ("Training Schedule",
         "This fictional schedule lists internal learning activities."),
        ("Team Directory",
         "This fictional directory contains sample employee information.")
    ],
    "IT": [
        ("Asset Inventory",
         "This fictional inventory summarizes sample IT equipment."),
        ("System Health Report",
         "This fictional report summarizes simulated system health."),
        ("Maintenance Schedule",
         "This fictional schedule records routine maintenance activities.")
    ],
    "Security": [
        ("Access Audit",
         "This fictional audit reviews sample access-control records."),
        ("Incident Summary",
         "This fictional summary describes a simulated security event."),
        ("Monitoring Report",
         "This fictional report summarizes simulated monitoring observations.")
    ],
    "Projects": [
        ("Project Status Report",
         "This fictional report tracks the status of an internal project."),
        ("Meeting Notes",
         "These fictional notes summarize a simulated project meeting."),
        ("Milestone Tracker",
         "This fictional tracker lists project milestones and progress.")
    ]
}


def load_lore():
    """Load the fictional company configuration."""
    if not LORE_PATH.exists():
        raise FileNotFoundError(
            f"Company lore file not found: {LORE_PATH}"
        )

    with LORE_PATH.open("r", encoding="utf-8") as file:
        lore = json.load(file)

    if not lore.get("company", {}).get("name"):
        raise ValueError("Company name is missing in company_lore.json")

    if not lore.get("file_generation", {}).get("default_directories"):
        raise ValueError("No departments configured in company_lore.json")

    return lore


def safe_name(value):
    """Convert a value into a safe filename component."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return cleaned.strip("_") or "document"


def generate_document(lore, department, rng):
    """Create fictional Markdown content for one department."""
    company = lore["company"]
    employees = lore.get("executives", [])
    projects = lore.get("fictional_projects", [])
    vocabulary = lore.get("corporate_vocabulary", [])

    templates = DOCUMENT_TEMPLATES.get(
        department,
        [("Department Summary", "This is a fictional department report.")]
    )

    title, summary = rng.choice(templates)
    author = rng.choice(employees) if employees else {
        "name": "Sample Employee",
        "role": "Department Coordinator"
    }

    project = rng.choice(projects) if projects else {
        "name": "Project Example",
        "description": "A fictional internal initiative",
        "status": "Planning"
    }

    phrase = rng.choice(vocabulary) if vocabulary else "routine review"
    status = rng.choice(["Draft", "In Review", "Completed"])
    reference = f"SIM-{rng.randint(1000, 9999)}"

    content = f"""# {title}

**Company:** {company['name']}  
**Department:** {department}  
**Document ID:** {reference}  
**Prepared by:** {author.get('name', 'Sample Employee')}  
**Role:** {author.get('role', 'Department Coordinator')}  
**Status:** {status}

## Overview

{summary}

This document is generated automatically by the PhantomNet
synthetic-document generator. All information is fictional and
intended for an isolated cybersecurity simulation.

## Department Notes

- Activity: {phrase}
- Related initiative: {project.get('name', 'Project Example')}
- Initiative status: {project.get('status', 'Planning')}
- Notes: {project.get('description', 'Fictional internal activity')}

## Action Items

1. Review the sample information.
2. Record any simulated observations.
3. Update the status during the next fictional review.

## Simulation Notice

This document contains synthetic data only. It must not be treated
as a real company record or used as evidence of an actual incident.
"""
    return title, content


def generate_documents(lore, count, seed=None):
    """Generate a list of fictional department documents."""
    if count < 1:
        raise ValueError("Count must be at least 1.")

    rng = random.Random(seed)
    departments = lore["file_generation"]["default_directories"]
    documents = []

    for number in range(1, count + 1):
        department = rng.choice(departments)
        title, content = generate_document(lore, department, rng)
        filename = (
            f"{safe_name(department)}_"
            f"{safe_name(title)}_{number:03d}.md"
        )
        documents.append((department, filename, content))

    return documents


def main():
    parser = argparse.ArgumentParser(
        description="Generate fictional corporate documents for PhantomNet."
    )
    parser.add_argument(
        "--count", type=int, default=5,
        help="Number of documents to generate (default: 5)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Optional seed for repeatable results"
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Save generated Markdown files under generated_docs/"
    )
    args = parser.parse_args()

    try:
        lore = load_lore()
        documents = generate_documents(
            lore, count=args.count, seed=args.seed
        )

        print(f"Company: {lore['company']['name']}")
        print(f"Generated {len(documents)} fictional documents.")

        if args.write:
            for department, filename, content in documents:
                folder = OUTPUT_DIR / safe_name(department)
                folder.mkdir(parents=True, exist_ok=True)

                output_path = folder / filename
                output_path.write_text(content, encoding="utf-8")
                print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")
        else:
            for department, filename, content in documents:
                print(f"\n{'=' * 60}")
                print(f"Department: {department}")
                print(f"Filename: {filename}")
                print("-" * 60)
                print(content)

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
