"""Smoke test the real Planner Agent using only its requirements artifact."""

import json
from pathlib import Path

from planner_agent import run_planner, validate_plan


def main():
    artifacts = Path(__file__).parent / "artifacts"
    requirements = json.loads((artifacts / "requirements.json").read_text(encoding="utf-8"))
    plan = validate_plan(run_planner(requirements))
    output = artifacts / "plan.json"
    output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Planner output saved to {output}:\n{output.read_text(encoding='utf-8')}")


if __name__ == "__main__":
    main()
