"""Read the plan artifact and save Qwen-generated Python navigation code."""

import json
from pathlib import Path

from developer_agent import run_developer


def main():
    directory = Path(__file__).parent
    with (directory / "artifacts" / "plan.json").open("r", encoding="utf-8") as file:
        plan = json.load(file)
    source = run_developer(plan)
    for output in (
        directory / "generated" / "navigation_logic.py",
        directory / "artifacts" / "navigation_logic.py",
        directory / "navigation_logic.py",
    ):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(source.rstrip() + "\n", encoding="utf-8")
        print(f"Navigation code saved to {output}")


if __name__ == "__main__":
    main()
