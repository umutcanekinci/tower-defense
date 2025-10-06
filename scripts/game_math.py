from pygame import Vector2

def distance(a: Vector2, b: Vector2):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

def angle_between_points(origin_point: Vector2, target_point: Vector2):
    return angle_between_delta(target_point - origin_point)

def angle_between_delta(delta: Vector2):
    return __angle_between(delta.y, delta.x)

def __angle_between(dy: float, dx: float):
    from math import atan2, degrees
    return degrees(atan2(dy, dx))

