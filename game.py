import random
import pygame
CELL = 20

class SnakeGame:
    def __init__(self, width=600, height=400):
        self.W = width
        self.H = height

        self.snake = [(100,100), (80,100), (60,100)]
        self.direction = (CELL, 0)
        
        self.obstacles = []
        self.food = self.spawn()
        self.poison = self.spawn()

        self.power = None
        self.power_spawn_time = 0
        self.power_active = None
        self.power_end = 0

        self.score = 0
        self.level = 1
        self.speed = 10


    def spawn(self):
        while True:
            x = random.randrange(0, self.W, CELL)
            y = random.randrange(0, self.H, CELL)
            if (x,y) not in self.snake and (x,y) not in self.obstacles:
                return (x,y)

    def spawn_power(self):
        types = ["speed","slow","shield"]
        self.power = (self.spawn(), random.choice(types))
        self.power_spawn_time = pygame.time.get_ticks()

    def spawn_obstacles(self):
        self.obstacles = []
        for _ in range(10):
            pos = self.spawn()
            self.obstacles.append(pos)

    def update(self):
        now = pygame.time.get_ticks()

        # power spawn
        if self.power is None:
            if random.randint(0,100) < 2:
                self.spawn_power()

        # power timeout
        if self.power and now - self.power_spawn_time > 8000:
            self.power = None

        # active power end
        if self.power_active and now > self.power_end:
            if self.power_active == "speed":
                self.speed = 10 + self.level
            elif self.power_active == "slow":
                self.speed = max(5, 10 + self.level - 3)
            self.power_active = None

        head = (self.snake[0][0] + self.direction[0],
                self.snake[0][1] + self.direction[1])

        # wall
        if head[0] < 0 or head[0] >= self.W or head[1] < 0 or head[1] >= self.H:
            if self.power_active == "shield":
                self.power_active = None
            else:
                return False

        # self
        if head in self.snake:
            if self.power_active == "shield":
                self.power_active = None
            else:
                return False

        # obstacles
        if head in self.obstacles:
            return False

        self.snake.insert(0, head)

        # food
        if head == self.food:
            self.score += 1
            self.food = self.spawn()

            if self.score % 5 == 0:
                self.level += 1
                self.speed += 1
                if self.level >= 3:
                    self.spawn_obstacles()
        else:
            self.snake.pop()

        # poison
        if head == self.poison:
            self.poison = self.spawn()
            if len(self.snake) > 2:
                self.snake.pop()
                self.snake.pop()
            if len(self.snake) <= 1:
                return False

        # power pickup
        if self.power and head == self.power[0]:
            t = self.power[1]
            self.power = None
            self.power_active = t
            self.power_end = now + 5000

            if t == "speed":
                self.speed += 5
            elif t == "slow":
                self.speed = max(3, self.speed - 5)
            elif t == "shield":
                pass

        return True