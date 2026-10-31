
import argparse
import json
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LORE_PATH = PROJECT_ROOT / "config" / "company_lore.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"


def load_company_lore():
    """Load fictional company information."""
    if not LORE_PATH.exists():
        raise FileNotFoundError("Company lore file not found.")

    with LORE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_prompt(lore, department, document_type):
    """Build a structured prompt for fictional documents."""

    company = lore["company"]

    projects = lore.get("fictional_projects", [])
    vocabulary = lore.get("corporate_vocabulary", [])
    executives = lore.get("executives", [])

    project_names = [
        item.get("name", "Sample Project")
        for item in projects
    ]

    employee_names = [
        item.get("name", "Sample Employee")
        for item in executives
    ]

    prompt = f"""
You are a document generator for PhantomNet,
an isolated cybersecurity research simulation.

Generate one fictional corporate document.

COMPANY INFORMATION:
Company: {company['name']}
Industry: {company.get('industry', 'Technology')}
Headquarters: {company.get('headquarters', 'Fictional Location')}

DOCUMENT DETAILS:
Department: {department}
Document Type: {document_type}

FICTIONAL REFERENCE DATA:
Projects: {', '.join(project_names)}
Sample Employees: {', '.join(employee_names)}
Corporate Vocabulary: {', '.join(vocabulary)}

OUTPUT STRUCTURE:
1. Document Title
2. Company and Department
3. Document Overview
4. Main Details
5. Three Action Items
6. Document Status

GENERATION RULES:
- Use professional corporate language.
- Keep the document internally consistent.
- Use only fictional information provided here or invented safely.
- Do not include real passwords, API keys, credentials,
  personal contact information, or real confidential data.
- Do not claim that this document belongs to a real company.
- Mark the document as SYNTHETIC SIMULATION DATA.
- Return Markdown only.
"""

    return prompt.strip()


def generate_document(prompt, model):
    """Send the prompt to the local Ollama model."""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_predict": 600
        }
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
        raise ValueError("The AI model returned empty content.")

    return content


def main():
    parser = argparse.ArgumentParser(
        description="PhantomNet prompt engineering module"
    )

    parser.add_argument(
        "--department",
        default="Security",
        help="Department for the fictional document"
    )

    parser.add_argument(
        "--type",
        default="Incident Summary",
        help="Type of fictional document"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Installed Ollama model"
    )

    args = parser.parse_args()

    try:
        lore = load_company_lore()

        departments = lore.get(
            "file_generation", {}
        ).get("default_directories", [])

        if args.department not in departments:
            raise ValueError(
                f"Choose a valid department: {departments}"
            )

        prompt = build_prompt(
            lore,
            args.department,
            args.type
        )

        print("\nGenerating fictional document...")
        print(f"Department: {args.department}")
        print(f"Document Type: {args.type}")

        result = generate_document(prompt, args.model)

        print("\n" + "=" * 60)
        print("PHANTOMNET GENERATED DOCUMENT")
        print("=" * 60)
        print(result)
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        parser.exit(
            status=1,
            message="Cannot connect to Ollama. Start Ollama first.\n"
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
        KeyError,
        ValueError
    ) as error:
        parser.exit(
            status=1,
            message=f"Error: {error}\n"
        )


if __name__ == "__main__":
    main()
