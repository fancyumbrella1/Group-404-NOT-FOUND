"""Behavioural tests for the generated public navigation entry point."""

from generated.navigation_logic import decide_next_move


ACTIONS = ("FORWARD", "LEFT", "RIGHT")


def state(goals=(False, False, False), blocked=(False, False, False)):
    return dict(zip(
        ("goal_ahead", "goal_on_left", "goal_on_right",
         "front_blocked", "left_blocked", "right_blocked"),
        (*goals, *blocked),
    ))


def test_known_states():
    cases = [
        (state((True, False, False)), "FORWARD"),
        (state((False, True, False)), "LEFT"),
        (state((False, False, True)), "RIGHT"),
        (state((True, False, False), (True, False, False)), "LEFT"),
        (state((False, True, False), (False, True, False)), "FORWARD"),
        (state((False, False, True), (True, False, True)), "LEFT"),
        (state((False, False, False), (True, True, False)), "RIGHT"),
        (state((False, False, False), (True, True, True)), "STOP"),
    ]
    for sensor_state, expected in cases:
        actual = decide_next_move(sensor_state)
        assert actual in (*ACTIONS, "STOP"), (sensor_state, actual)
        assert actual == expected, (sensor_state, expected, actual)


def test_all_sensor_states():
    """Eight goal patterns times eight obstacle patterns: 64 total states."""
    for goal_bits in range(8):
        goals = tuple(bool(goal_bits & (1 << i)) for i in range(3))
        for blocked_bits in range(8):
            blocked = tuple(bool(blocked_bits & (1 << i)) for i in range(3))
            sensor_state = state(goals, blocked)
            safe_goals = [move for move, wanted, obstacle in zip(ACTIONS, goals, blocked)
                          if wanted and not obstacle]
            safe_moves = [move for move, obstacle in zip(ACTIONS, blocked) if not obstacle]
            expected = (safe_goals[0] if safe_goals else
                        safe_moves[0] if safe_moves else "STOP")
            actual = decide_next_move(sensor_state)
            assert actual in (*ACTIONS, "STOP"), (sensor_state, actual)
            assert actual == expected, (sensor_state, expected, actual)


if __name__ == "__main__":
    test_known_states()
    test_all_sensor_states()
    print("Navigation behaviour passed: 8 named cases and all 64 sensor states.")
