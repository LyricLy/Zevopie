import math


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, vec):
        self.x += vec.x
        self.y += vec.y

    def distance(self, other):
        return Vector(other.x - self.x, other.y - self.y).magnitude

    # faster than comparison with distance
    def in_distance(self, dist, other):
        return Vector(other.x - self.x, other.y - self.y).sqr_magnitude < dist ** 2

    def copy(self):
        return type(self)(self.x, self.y)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def magnitude(self):
        return math.hypot(self.x, self.y)

    @property
    def sqr_magnitude(self):
        return self.x ** 2 + self.y ** 2

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    @classmethod
    def from_angle(cls, angle, speed=1):
        return cls(math.cos(angle) * speed, math.sin(angle) * speed)

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return type(self)(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        self.x *= other
        self.y *= other

    def __rmul__(self, other):
        self.__mul__(other)

    def __matmul__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.x * other.x + self.y * other.y