# Testing record

Group: 404 NOT FOUND

The three smoke tests ran the real local `qwen3:8b` model through Ollama. The
Analyst saved and displayed `artifacts/requirements.json`; the Planner saved
and displayed `artifacts/plan.json`; the Developer saved and displayed the
validated generated code in `generated/navigation_logic.py` and the two
compatibility paths documented in the README.

An early Developer output failed validation because it chose a fallback move
while another goal direction was safe. A later Planner output incorrectly
paired an unknown or blocked goal with STOP. The prompts and plan validation
were tightened, and the agents were rerun. The final plan stops only when all
three directions are blocked; the final generated code passed validation.

The behavioural test passed eight named cases and all 64 combinations of
three goal flags and three blocked-direction flags.

To check that the tests detect a real error, the first `return "FORWARD"` in
the generated file was temporarily changed to `return "LEFT"`. The test then
failed: with a clear front path and a goal ahead, it expected `FORWARD` but
received `LEFT`. The original code was restored immediately, and the same
test passed again. No intentional bug remains in the submitted code.
