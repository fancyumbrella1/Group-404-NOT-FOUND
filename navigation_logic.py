def choose_action(front_blocked, left_blocked, right_blocked, goal_direction=None):
    if goal_direction == "FORWARD" and not front_blocked:
        return "FORWARD"
    if goal_direction == "LEFT" and not left_blocked:
        return "LEFT"
    if goal_direction == "RIGHT" and not right_blocked:
        return "RIGHT"
    if front_blocked and left_blocked and right_blocked:
        return "STOP"
    if not front_blocked:
        return "FORWARD"
    if not left_blocked:
        return "LEFT"
    if not right_blocked:
        return "RIGHT"
    return "STOP"
