import ball
import pygame
import sys

from pos_vec import Position


class Game:
    def __init__(self, size, balls):
        self.size = size
        self.display = pygame.display.set_mode(size)
        self.balls = [cls(self, pos) for cls, pos in balls]

    def start(self):
        clock = pygame.time.Clock()
        while True:
            self.display.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)

            for ball in self.balls:
                ball.step()

            pygame.display.flip()
            clock.tick(60)


game = Game((1280, 720), [(ball.Player, Position(640, 360))])
game.start()
