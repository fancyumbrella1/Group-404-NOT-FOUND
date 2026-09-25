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
contains the goal, even if the front path is clear but the goal is to a side.
If multiple goal flags are present, choose the first safe goal direction in
this fixed order: FORWARD, LEFT, RIGHT. If no indicated goal direction is
safe, choose the first safe direction in the same order.
Stop only when front, left, and right are all blocked.
Return only one valid JSON object, without markdown or commentary:
{
  "strategy": "nonempty explanation of the navigation priority",
  "decisions": [
    {"condition": "Goal ahead is safe", "action": "FORWARD"},
    {"condition": "Goal left is safe", "action": "LEFT"},
    {"condition": "Goal right is safe", "action": "RIGHT"},
    {"condition": "No safe goal and front is clear", "action": "FORWARD"},
    {"condition": "No safe goal, front blocked, left clear", "action": "LEFT"},
    {"condition": "No safe goal, front and left blocked, right clear", "action": "RIGHT"},
    {"condition": "All three directions are blocked", "action": "STOP"}
  ],
  "stop_condition": "nonempty description of when STOP is required"
}
Include decisions for a clear front goal, a clear left goal even when front
is clear, a clear right goal even when front is clear, fallback when a goal
direction is blocked or unknown, and STOP when all directions are blocked.
The STOP decision must use this exact condition text:
"All three directions are blocked".
Never pair STOP with a blocked or unknown goal direction alone. A blocked or
unknown goal still requires a safe fallback if any direction is unblocked.
Cover all four allowed actions. Do not add other keys."""


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
        if decision["action"] == "STOP":
            condition = decision["condition"].casefold()
            if "all" not in condition or "block" not in condition:
                raise ValueError("STOP is allowed only when all directions are blocked.")
        actions.add(decision["action"])
    if actions != {"FORWARD", "LEFT", "RIGHT", "STOP"}:
        raise ValueError("The plan must cover every allowed action.")
    return data


def run_planner(requirement):
    validate_requirements(requirement)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(requirement, ensure_ascii=False)},
    ]
    for attempt in range(4):
        response = chat(model=MODEL, format="json", think=False, messages=messages)
        raw = response.message.content
        try:
            return validate_plan(json.loads(raw))
        except (ValueError, json.JSONDecodeError) as error:
            if attempt == 3:
                raise ValueError(f"Qwen produced an invalid plan: {error}\nLast JSON:\n{raw}") from error
            messages.extend([
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"Fix this error: {error}. Return only corrected JSON."},
            ])
