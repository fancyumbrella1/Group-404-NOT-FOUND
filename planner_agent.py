"""Turn validated requirements into a structured navigation plan."""

import json
import os

from ollama import chat

from analyst_agent import validate_requirements


MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
SYSTEM_PROMPT = """You are the Planner Agent for a mobile robot.
You receive only the validated requirements artifact, not earlier conversation.
Decide how the robot should behave. Use only FORWARD, LEFT, RIGHT, and STOP.
Never plan to move into a blocked direction. Prefer a safe direction that
contains the goal. If the goal is unknown or its direction is blocked, choose
the first safe direction in this fixed order: FORWARD, LEFT, RIGHT.
Stop only when front, left, and right are all blocked.
Return only one valid JSON object, without markdown or commentary:
{
  "strategy": "nonempty explanation of the navigation priority",
  "decisions": [
    {"condition": "nonempty situation description", "action": "FORWARD"}
  ],
  "stop_condition": "nonempty description of when STOP is required"
}
Include decisions covering all four allowed actions. Do not add other keys."""


def validate_plan(data):
    if not isinstance(data, dict) or set(data) != {
        "strategy", "decisions", "stop_condition"
    }:
        raise ValueError("Plan must contain exactly strategy, decisions, stop_condition.")
    if not isinstance(data["strategy"], str) or not data["strategy"].strip():
        raise ValueError("strategy must be a nonempty string.")
    if not isinstance(data["stop_condition"], str) or not data["stop_condition"].strip():
        raise ValueError("stop_condition must be a nonempty string.")
    decisions = data["decisions"]
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decisions must be a nonempty list.")
    actions = set()
    for decision in decisions:
        if not isinstance(decision, dict) or set(decision) != {"condition", "action"}:
            raise ValueError("Each decision needs exactly condition and action.")
        if not isinstance(decision["condition"], str) or not decision["condition"].strip():
            raise ValueError("Each condition must be a nonempty string.")
        if decision["action"] not in {"FORWARD", "LEFT", "RIGHT", "STOP"}:
            raise ValueError("A decision contains an invalid action.")
        actions.add(decision["action"])
    if actions != {"FORWARD", "LEFT", "RIGHT", "STOP"}:
        raise ValueError("The plan must cover every allowed action.")
    return data


def run_planner(requirement):
    validate_requirements(requirement)
    response = chat(
        model=MODEL,
        format="json",
        think=False,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(requirement, ensure_ascii=False)},
        ],
    )
    return validate_plan(json.loads(response.message.content))
