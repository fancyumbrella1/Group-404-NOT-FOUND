"""Smoke test the real Developer Agent using only its plan artifact."""

import json
from pathlib import Path

from developer_agent import run_developer, validate_code


def main():
    root = Path(__file__).parent
    plan = json.loads((root / "artifacts" / "plan.json").read_text(encoding="utf-8"))
    source = validate_code(run_developer(plan)).rstrip() + "\n"
    for output in (
        root / "generated" / "navigation_logic.py",
        root / "artifacts" / "navigation_logic.py",
        root / "navigation_logic.py",
    ):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(source, encoding="utf-8")
        print(f"Developer output saved to {output}")
    print(source)


if __name__ == "__main__":
    main()
