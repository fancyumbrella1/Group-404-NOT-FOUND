"""Smoke test the real Analyst Agent against the original brief."""

import json
from pathlib import Path

from analyst_agent import run_analyst, validate_requirements


def main():
    root = Path(__file__).parent
    brief = (root / "brief.txt").read_text(encoding="utf-8")
    requirements = validate_requirements(run_analyst(brief))
    output = root / "artifacts" / "requirements.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(requirements, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Analyst output saved to {output}:\n{output.read_text(encoding='utf-8')}")


if __name__ == "__main__":
    main()
