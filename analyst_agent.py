"""Convert the human robot brief into validated software requirements."""

import json
import os

from ollama import chat


MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
SYSTEM_PROMPT = """You are the Analyst Agent for a mobile robot.
Read the human brief and extract explicit software requirements.
Return only one valid JSON object with exactly these keys and types:
{
  "goal": "a concise description of the navigation objective",
  "allowed_actions": ["FORWARD", "LEFT", "RIGHT", "STOP"],
  "safe_stop": true,
  "avoid_obstacles": true
}
Use only the brief. Do not add actions, keys, markdown, or commentary."""


def validate_requirements(data):
    if not isinstance(data, dict) or set(data) != {
        "goal", "allowed_actions", "safe_stop", "avoid_obstacles"
    }:
        raise ValueError("Requirements must contain exactly the four required keys.")
    if not isinstance(data["goal"], str) or not data["goal"].strip():
        raise ValueError("goal must be a nonempty string.")
    if data["allowed_actions"] != ["FORWARD", "LEFT", "RIGHT", "STOP"]:
        raise ValueError("allowed_actions must contain only the four specified actions.")
    if data["safe_stop"] is not True or data["avoid_obstacles"] is not True:
        raise ValueError("safe_stop and avoid_obstacles must be true booleans.")
    return data


def run_analyst(brief_text):
    if not isinstance(brief_text, str) or not brief_text.strip():
        raise ValueError("The brief must be nonempty text.")
    response = chat(
        model=MODEL,
        format="json",
        think=False,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": brief_text},
        ],
    )
    return validate_requirements(json.loads(response.message.content))
