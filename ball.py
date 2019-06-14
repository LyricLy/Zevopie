import copy
import pygame

from network import Network, Node
from pos_vec import Position, Vector


POWER_RATIO = 20

class Ball:
    def __init__(self, game, pos, vec=None, radius=2):
        self.game = game
        self.width, self.height = game.size
        self.pos = pos
        self.vec = vec or Vector(0, 0)
        self.radius = radius

    def move(self, friction):
        self.pos.move(self.vec)
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > self.width:
            self.pos.x = min(max(self.pos.x, self.radius), self.height - self.radius)
            self.vec.x *= -0.25
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > self.height:
            self.pos.y = min(max(self.pos.y, self.radius), self.height - self.radius)
            self.vec.y *= -0.25
        self.vec = Vector.from_angle(self.vec.angle, max(self.vec.magnitude - friction, 0))

    def draw(self, colour):
        if self.game.draw:
            pygame.draw.circle(self.game.display,
                               colour,
                               (int(self.pos.x), int(self.pos.y)),
                               self.radius)


class AI(Ball):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game.pop += 1
        self.generation = 0
        self.net = Network([[Node() for _ in range(5)], [Node() for _ in range(5)]], 4)
        self.bomb_time = 0
        self.energy = 300

    def step(self):
        nearest_food, sqr_dist = None, float("inf")
        for b in self.game.balls:
            if isinstance(b, Food):
                d = (b.pos - self.pos).sqr_magnitude
                if d < sqr_dist:
                    nearest_food = b
                    sqr_dist = d

        if nearest_food and sqr_dist < (self.radius + nearest_food.radius) ** 2:
            self.energy += 120
            self.game.balls.remove(nearest_food)
            new_ai = copy.copy(self.net)
            new_ai.mutate()
            new_ball = AI(self.game, self.pos.copy(), radius=self.radius)
            new_ball.net = new_ai
            new_ball.generation = self.generation + 1
            self.game.balls.append(new_ball)

        nearest_vec = nearest_food.pos - self.pos if nearest_food else Vector(0, 0)
        fire, fx, fy, fuse, power = self.net.evaluate([
            self.vec.x,
            self.vec.y,
            nearest_vec.x,
            nearest_vec.y
        ])

        b = 2
        fx = min(max(fx, -b), b)
        fy = min(max(fy, -b), b)
        power = min(max(power, 0), 2)

        if fire > 0 and self.bomb_time > 5:
            self.energy -= 5
            self.bomb_time = 0
            self.game.balls.append(Bomb(fuse, power, self.game, self.pos.copy(), Vector(fx, fy)))

        self.energy -= 1
        if self.energy <= 0:
            self.game.balls.remove(self)
            self.game.pop -= 1

        self.bomb_time += 1

        self.move(0.2)
        self.draw((0, 0, 0))


class Bomb(Ball):
    def __init__(self, fuse, power, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fuse = fuse
        self.power = power * self.radius
        self.ratio = POWER_RATIO * self.radius

    def step(self):
        self.fuse -= 1
        if self.fuse <= 0:
            for ball in self.game.balls:
                if ball is not self and self.pos.in_distance(self.power * self.ratio, ball.pos):
                    vec = Vector(ball.pos.x - self.pos.x, ball.pos.y - self.pos.y)
                    dist = self.pos.distance(ball.pos)
                    ball.vec += Vector.from_angle(vec.angle, self.power - dist / self.ratio)
            self.game.balls.remove(self)

        self.move(0.4)
        self.draw((255, 0, 0))


class Food(Ball):
    def step(self):
        self.move(1.0)
        self.draw((0, 255, 0))
