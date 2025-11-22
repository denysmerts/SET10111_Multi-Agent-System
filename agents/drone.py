from .agent import Agent
import random

DRONE_VISION_RADIUS = 5  # <= drone only "sees" within 3 cells


class Drone(Agent):
    """
    Drone agent:
    - Moves faster than ground searchers
    - Can fly over obstacles (ignores env blocks)
    - Has a limited vision radius (3 cells)
    """
    def __init__(self, id_, x, y, vision_radius: int = DRONE_VISION_RADIUS):
        super().__init__(id_, x, y)
        self.vision_radius = vision_radius
        self.has_found = False
        self.steps_taken = 0

    def neighbours(self, env):
        # Drone ignores obstacles — can move anywhere inside grid
        moves = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1),
        ]

        result = []
        for x, y in moves:
            if 0 <= x < env.width and 0 <= y < env.height:
                result.append((x, y))
        return result

    def step(self, env):
        if self.has_found:
            return

        # Drone moves 2 steps per tick
        for _ in range(2):
            options = self.neighbours(env)
            if not options:
                return
            self.x, self.y = random.choice(options)
            self.steps_taken += 1

    def detect_casualty(self, casualty):
        # Only detect when casualty is within DRONE_VISION_RADIUS
        dist = abs(self.x - casualty.x) + abs(self.y - casualty.y)
        if dist <= self.vision_radius:
            self.has_found = True
            return True
        return False
