"""Read the requirements artifact and save the Qwen-generated plan."""

import json
from pathlib import Path

from planner_agent import run_planner


def main():
    artifacts = Path(__file__).parent / "artifacts"
    with (artifacts / "requirements.json").open("r", encoding="utf-8") as file:
        requirements = json.load(file)
    plan = run_planner(requirements)
    with (artifacts / "plan.json").open("w", encoding="utf-8") as file:
        json.dump(plan, file, indent=2, ensure_ascii=False)
    print(f"Plan saved to {artifacts / 'plan.json'}")


if __name__ == "__main__":
    main()
