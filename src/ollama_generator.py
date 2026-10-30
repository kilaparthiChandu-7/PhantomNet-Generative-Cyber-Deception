
import argparse
import json
import re
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LORE_PATH = PROJECT_ROOT / "config" / "company_lore.json"
OUTPUT_DIR = PROJECT_ROOT / "generated_docs"

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"


def load_lore():
    """Load fictional company information."""
    if not LORE_PATH.exists():
        raise FileNotFoundError("config/company_lore.json was not found.")

    with LORE_PATH.open("r", encoding="utf-8") as file:
        lore = json.load(file)

    if not lore.get("company", {}).get("name"):
        raise ValueError("Company name is missing.")

    return lore


def safe_filename(value):
    """Create a safe filename."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return cleaned.strip("_") or "document"


def generate_with_ollama(lore, department, model):
    """Ask the local Ollama model to generate fictional content."""
    company = lore["company"]
    projects = lore.get("fictional_projects", [])
    vocabulary = lore.get("corporate_vocabulary", [])

    project_names = [
        project.get("name", "Sample Project")
        for project in projects
    ]

    prompt = f"""
You are generating fictional documents for a cybersecurity
deception research simulator named PhantomNet.

Create a realistic but entirely fictional corporate document.

Company: {company['name']}
Industry: {company.get('industry', 'Technology')}
Department: {department}
Fictional projects: {', '.join(project_names)}
Corporate vocabulary: {', '.join(vocabulary)}

Requirements:
1. Give the document a suitable title.
2. Include an overview and department-specific notes.
3. Include three fictional action items.
4. Use only invented names and sample information.
5. Do not include real passwords, API keys, personal data,
   real credentials, or actual confidential information.
6. Clearly mark the document as SYNTHETIC SIMULATION DATA.
7. Return Markdown content only.
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()
    result = response.json()

    content = result.get("response", "").strip()

    if not content:
        raise ValueError("Ollama returned empty content.")

    return content


def save_document(department, content):
    """Save generated content inside the simulation folder."""
    folder = (OUTPUT_DIR / safe_filename(department)).resolve()

    if not folder.is_relative_to(OUTPUT_DIR.resolve()):
        raise ValueError("Invalid output directory.")

    folder.mkdir(parents=True, exist_ok=True)

    filename = f"ollama_document_{len(list(folder.glob('ollama_document_*.md'))) + 1:03d}.md"
    output_path = folder / filename

    output_path.write_text(content, encoding="utf-8")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate fictional documents using local Ollama."
    )

    parser.add_argument(
        "--department",
        default="Security",
        help="Department for the fictional document"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Installed Ollama model name"
    )

    parser.add_argument(
        "--write",
        action="store_true",
        help="Save the generated document locally"
    )

    args = parser.parse_args()

    try:
        lore = load_lore()

        departments = lore.get(
            "file_generation", {}
        ).get("default_directories", [])

        if args.department not in departments:
            raise ValueError(
                f"Unknown department. Choose from: {departments}"
            )

        print("Connecting to local Ollama...")
        print(f"Model: {args.model}")
        print(f"Department: {args.department}")

        content = generate_with_ollama(
            lore, args.department, args.model
        )

        print("\n--- Generated Fictional Document ---\n")
        print(content)

        if args.write:
            output_path = save_document(args.department, content)
            print(f"\nSaved document: {output_path}")

    except requests.exceptions.ConnectionError:
        parser.exit(
            status=1,
            message="Could not connect to Ollama. Make sure Ollama is running.\n"
        )
    except requests.exceptions.Timeout:
        parser.exit(
            status=1,
            message="Ollama request timed out. Try again.\n"
        )
    except requests.exceptions.HTTPError as error:
        parser.exit(
            status=1,
            message=f"Ollama API error: {error}\n"
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
        OSError
    ) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
