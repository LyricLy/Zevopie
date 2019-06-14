import ball
import pygame
import random
import sys

from pos_vec import Position


KEEP_AT = 40

class Game:
    def __init__(self, size):
        self.size = size
        self.display = pygame.display.set_mode(size)
        self.balls = []
        self.draw = True
        self.pop = 0
        self.best_generation = 0

    def start(self):
        clock = pygame.time.Clock()
        food_clock = 0
        while True:
            if self.pop < KEEP_AT:
                self.balls.extend([ball.AI(self, Position(random.randint(0, 1280), random.randint(0, 720))) for _ in range(KEEP_AT - self.pop)])

            self.display.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == 100:  # d
                        self.draw = not self.draw

            for b in self.balls:
                b.step()

            if food_clock == 0:
                print(f"best generation so far: {self.best_generation}")
                self.balls.append(ball.Food(self, Position(random.randint(0, 1280), random.randint(0, 720))))
                food_clock = 60
            food_clock -= 1

            if self.draw:
                pygame.display.flip()
                clock.tick(60)


game = Game((1280, 720))
game.start()
