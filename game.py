import pygame
import random

WIDTH, HEIGHT = 600, 400
CELL = 20

class SnakeGame:
    def __init__(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = (CELL, 0)
        self.food = self.spawn_food()
        self.poison = self.spawn_food()

        self.score = 0
        self.level = 1
        self.speed = 10

    def spawn_food(self):
        return (random.randrange(0, WIDTH, CELL),
                random.randrange(0, HEIGHT, CELL))

    def update(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0],
                    head[1] + self.direction[1])

        # стены
        if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            return False

        # в себя
        if new_head in self.snake:
            return False

        self.snake.insert(0, new_head)

        # обычная еда
        if new_head == self.food:
            self.score += 1

            if self.score % 5 == 0:
                self.level += 1
                self.speed += 2

            self.food = self.spawn_food()
        else:
            self.snake.pop()

        # poison
        if new_head == self.poison:
            self.snake = self.snake[:-2]
            if len(self.snake) <= 1:
                return False
            self.poison = self.spawn_food()

        return True