import pygame

from pos_vec import Position, Vector


class Ball:
    def __init__(self, game, pos, vec=None, radius=5):
        self.game = game
        self.width, self.height = game.size
        self.pos = pos
        self.vec = vec or Vector(0, 0)
        self.radius = radius

    def move(self):
        self.pos.move(self.vec)
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > self.width:
            self.vec.x *= -1
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > self.height:
            self.vec.y *= -1

    def draw(self, colour):
        pygame.draw.circle(self.game.display,
                           colour,
                           (int(self.pos.x), int(self.pos.y)),
                           self.radius)


class Player(Ball):
    def step(self):
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            vec = Vector(mx - self.pos.x, my - self.pos.y)
            self.vec += Vector.from_angle(vec.angle, 0.1)
        if pygame.mouse.get_pressed()[2]:
            if not self.last:
                mx, my = pygame.mouse.get_pos()
                vec = Vector(mx - self.pos.x, my - self.pos.y)
                bomb_vec = Vector.from_angle(vec.angle, 0.1)
                self.game.balls.append(Bomb(60, 50, self.game, self.pos.copy(), bomb_vec))
                self.last = True
        else:
            self.last = False

        self.move()
        self.draw((0, 0, 0))


class Bomb(Ball):
    def __init__(self, fuse, power, *args):
        super().__init__(*args)
        self.fuse = fuse
        self.power = power

    def step(self):
        self.fuse -= 1
        if self.fuse <= 0:
            for ball in self.game.balls:
                if ball is not self and self.pos.in_distance(self.power, ball.pos):
                    vec = Vector(ball.pos.x - self.pos.x, ball.pos.y - self.pos.y)
                    dist = self.pos.distance(ball.pos)
                    ball.vec += Vector.from_angle(vec.angle, (self.power - dist) / 10)
            self.game.balls.remove(self)

        self.move()
        self.draw((255, 0, 0))
