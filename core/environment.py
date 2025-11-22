import random
from dataclasses import dataclass

@dataclass
class Cell:
    x: int
    y: int

class Environment:
    def __init__(self, width, height, obstacle_ratio=0.08):
        self.width = width
        self.height = height
        self.obstacles = self._generate_obstacles(obstacle_ratio)

    def _generate_obstacles(self, ratio):
        obstacles = []
        total = self.width * self.height
        count = int(total * ratio)

        while len(obstacles) < count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in obstacles:
                obstacles.append((x, y))
        return obstacles

    def is_free(self, x, y):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        return (x, y) not in self.obstacles

    def random_free_cell(self):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.is_free(x, y):
                return Cell(x, y)
