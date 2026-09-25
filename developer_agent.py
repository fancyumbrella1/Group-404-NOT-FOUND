"""Generate and validate the final robot navigation function."""

import ast
import json
import os

from ollama import chat

from planner_agent import validate_plan


MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
SYSTEM_PROMPT = """You are the Developer Agent for a mobile robot.
You receive only the validated plan JSON, not previous agent conversations.
Return only Python source code, with no markdown fences or explanation.
Define exactly this function:
def choose_action(front_blocked, left_blocked, right_blocked, goal_direction=None):
The first three arguments are booleans. goal_direction is FORWARD, LEFT,
RIGHT, or None. Return only the strings FORWARD, LEFT, RIGHT, or STOP.
If a goal direction is known and unblocked, choose it. Otherwise choose
the first unblocked direction in this order: FORWARD, LEFT, RIGHT.
Return STOP only if all three directions are blocked.
Use only if statements, boolean expressions, and literal return strings.
Do not import, call functions, use loops, access attributes, or perform I/O."""

_ARGUMENTS = ["front_blocked", "left_blocked", "right_blocked", "goal_direction"]
_ACTIONS = ("FORWARD", "LEFT", "RIGHT")
_ALLOWED_NODES = (
    ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.If, ast.Return,
    ast.BoolOp, ast.UnaryOp, ast.Compare, ast.Name, ast.Load, ast.Constant,
    ast.And, ast.Or, ast.Not, ast.Eq, ast.Is, ast.IsNot,
)


def validate_code(source):
    """Check syntax, limit executable constructs, and verify every input case."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Generated code must be nonempty Python source.")
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError(f"Invalid Python syntax: {error}") from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Source must contain exactly one function definition.")
    function = tree.body[0]
    arguments = function.args
    if function.name != "choose_action" or [arg.arg for arg in arguments.args] != _ARGUMENTS:
        raise ValueError("Function name or parameters do not match the required interface.")
    if (len(arguments.defaults) != 1 or not isinstance(arguments.defaults[0], ast.Constant)
            or arguments.defaults[0].value is not None or arguments.posonlyargs
            or arguments.kwonlyargs or arguments.vararg or arguments.kwarg
            or function.decorator_list or function.returns):
        raise ValueError("The function signature contains unsupported features.")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Unsupported Python construct: {type(node).__name__}.")
        if isinstance(node, ast.Name) and node.id not in _ARGUMENTS:
            raise ValueError(f"Unexpected name: {node.id}.")
        if isinstance(node, ast.Constant) and node.value not in (*_ACTIONS, "STOP", None):
            # Python treats True == 1, so test types separately.
            if type(node.value) is not bool:
                raise ValueError("Unexpected literal in generated code.")

    namespace = {}
    exec(compile(tree, "<generated-navigation>", "exec"), {"__builtins__": {}}, namespace)
    choose_action = namespace["choose_action"]
    for bits in range(8):
        blocked = tuple(bool(bits & (1 << index)) for index in range(3))
        for goal in (None, *_ACTIONS):
            safe = [action for action, is_blocked in zip(_ACTIONS, blocked) if not is_blocked]
            expected = goal if goal in safe else (safe[0] if safe else "STOP")
            try:
                actual = choose_action(*blocked, goal)
            except Exception as error:
                raise ValueError(f"Generated function failed for {blocked}, {goal}: {error}") from error
            if actual != expected:
                raise ValueError(
                    f"Wrong action for blocked={blocked}, goal={goal}: "
                    f"expected {expected}, got {actual}."
                )
    return source


def run_developer(plan):
    """Ask Qwen for code and retry if it fails validation."""
    validate_plan(plan)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(plan, ensure_ascii=False)},
    ]
    for attempt in range(3):
        response = chat(model=MODEL, think=False, messages=messages)
        source = response.message.content.strip()
        try:
            return validate_code(source)
        except ValueError as error:
            if attempt == 2:
                raise ValueError(f"Qwen produced invalid navigation code: {error}") from error
            messages.extend([
                {"role": "assistant", "content": source},
                {"role": "user", "content": f"Fix this validation error: {error}. Return only corrected Python code."},
            ])
