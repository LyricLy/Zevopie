import pygame

from network import Network, Node
from pos_vec import Position, Vector


POWER_RATIO = 20

class Ball:
    def __init__(self, game, pos, vec=None, radius=5):
        self.game = game
        self.width, self.height = game.size
        self.pos = pos
        self.vec = vec or Vector(0, 0)
        self.radius = radius

    def move(self, friction):
        self.pos.move(self.vec)
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > self.width:
            self.vec.x *= -1
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > self.height:
            self.vec.y *= -1
        self.vec = Vector.from_angle(self.vec.angle, max(self.vec.magnitude - friction, 0))

    def draw(self, colour):
        if self.game.draw:
            pygame.draw.circle(self.game.display,
                               colour,
                               (int(self.pos.x), int(self.pos.y)),
                               self.radius)


class AI(Ball):
    def __init__(self, *args):
        super().__init__(*args)
        self.net = Network([[Node() for _ in range(6)], [Node() for _ in range(5)]], 7)
        self.bomb_time = 0
        self.energy = 20 * 120

    def step(self):
        fire, fx, fy, fuse, power = self.net.evaluate([1, self.vec.x, self.vec.y, 0, 0, self.energy / 20, self.bomb_time])
        if fire > 0:
            self.energy -= 120
            self.bomb_time = 0
            self.game.balls.append(Bomb(fuse * 120, max(power, 0), self.game, self.pos.copy(), Vector(fx, fy)))

        self.energy -= 1
        if self.energy <= 0:
            self.game.balls.remove(self)
        self.bomb_time += 1

        self.move(0.1)
        self.draw((0, 0, 0))


class Bomb(Ball):
    def __init__(self, fuse, power, *args):
        super().__init__(*args)
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
        self.move(0.3)
        self.draw((0, 255, 0))
