import copy
import pygame

from network import Network, Node
from pos_vec import Position, Vector


POWER_RATIO = 20

class Ball:
    def __init__(self, game, pos, vec=None, radius=3):
        self.game = game
        self.width, self.height = game.size
        self.pos = pos
        self.vec = vec or Vector(0, 0)
        self.radius = radius

    def move(self, friction):
        self.pos.move(self.vec)
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > self.width:
            self.pos.x = min(max(self.pos.x, self.radius), self.height - self.radius)
            self.vec.x *= -0.2
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > self.height:
            self.pos.y = min(max(self.pos.y, self.radius), self.height - self.radius)
            self.vec.y *= -0.2
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
        self.net = Network([[Node() for _ in range(6)], [Node() for _ in range(5)]], 7)
        self.bomb_time = 0
        self.energy = 20 * 60
        self.birth_timer = 60

    def step(self):
        nearest_food, sqr_dist = None, float("inf")
        for b in self.game.balls:
            if isinstance(b, Food):
                d = (b.pos - self.pos).sqr_magnitude
                if d < sqr_dist:
                    nearest_food = b
                    sqr_dist = d

        if nearest_food and sqr_dist < (self.radius + nearest_food.radius) ** 2:
            self.energy += 10 * 60
            self.game.balls.remove(nearest_food)

        nearest_vec = nearest_food.pos - self.pos if nearest_food else Vector(0, 0)
        fire, fx, fy, fuse, power = self.net.evaluate([
            1,
            self.vec.x,
            self.vec.y,
            nearest_vec.x,
            nearest_vec.y,
            self.energy / 20,
            self.bomb_time
        ])
        if fire > 0:
            self.energy -= 20
            self.bomb_time = 0
            self.game.balls.append(Bomb(fuse * 120, max(power, 0), self.game, self.pos.copy(), Vector(fx, fy)))

        self.energy -= 1
        if self.energy <= 0:
            self.game.balls.remove(self)
            self.game.pop -= 1
        elif self.energy >= 20 * 120:
            self.birth_timer -= 1
            if not self.birth_timer:
                self.energy -= 20 * 120
                new_ai = copy.copy(self.net)
                new_ai.mutate()
                new_ball = AI(self.game, self.pos.copy(), radius=self.radius)
                new_ball.net = new_ai
                new_ball.generation = self.generation + 1
                if new_ball.generation > self.game.best_generation:
                    self.game.best_generation = new_ball.generation
                self.game.balls.append(new_ball)
                self.birth_timer = 60
        else:
            self.birth_timer = 60

        self.bomb_time += 1

        self.move(0.1)
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

        self.move(0.1)
        self.draw((255, 0, 0))


class Food(Ball):
    def step(self):
        self.move(0.5)
        self.draw((0, 255, 0))
