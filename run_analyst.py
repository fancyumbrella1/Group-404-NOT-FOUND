"""Run the Analyst Agent and save its requirements artifact."""

import json
from pathlib import Path

from analyst_agent import run_analyst


def main():
    root = Path(__file__).parent
    brief = (root / "brief.txt").read_text(encoding="utf-8")
    requirements = run_analyst(brief)
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    output = artifacts / "requirements.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(requirements, file, indent=2, ensure_ascii=False)
    print(f"Requirements saved to {output}")


if __name__ == "__main__":
    main()
