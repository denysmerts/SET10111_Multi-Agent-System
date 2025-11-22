import random
from .agent import Agent


class Searcher(Agent):
    def __init__(self, id_, x, y, vision_radius=0):
        super().__init__(id_, x, y)
        self.vision_radius = vision_radius

        self.has_found = False
        self.steps_taken = 0

        self.visited = {self.pos}
        self.last_pos = None

        # Communication / rescue mode
        self.mode = "search"          # "search" or "rescue"
        self.target = None            # (x, y)

    # -----------------------------------------
    # Utility: get free neighbouring cells
    # -----------------------------------------
    def neighbours(self, env):
        candidates = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1),
        ]
        return [(x, y) for (x, y) in candidates if env.is_free(x, y)]

    # -----------------------------------------
    # MAIN STEP FUNCTION  (FIXED & CLEAN)
    # -----------------------------------------
    def step(self, env):
        # Stop moving if already found something
        if self.has_found:
            return

        # -----------------------------------------
        # RESCUE MODE — move toward casualty
        # -----------------------------------------
        if self.mode == "rescue" and self.target:
            tx, ty = self.target

            dx = tx - self.x
            dy = ty - self.y

            # Move one step toward target
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0

            new_x = self.x + move_x
            new_y = self.y + move_y

            # If direction is free → move there
            if env.is_free(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.steps_taken += 1
                return

            # Otherwise fallback to random neighbour
            options = self.neighbours(env)
            if options:
                self.x, self.y = random.choice(options)
                self.steps_taken += 1
            return

        # -----------------------------------------
        # SEARCH MODE — random walk
        # -----------------------------------------
        options = self.neighbours(env)
        if not options:
            return

        # Prefer unvisited cells
        unvisited = [pos for pos in options if pos not in self.visited]
        chosen = random.choice(unvisited) if unvisited else random.choice(options)

        # Prevent oscillation
        if self.last_pos and chosen == self.last_pos and len(options) > 1:
            alternatives = [p for p in options if p != self.last_pos]
            chosen = random.choice(alternatives)

        # Apply movement
        self.last_pos = (self.x, self.y)
        self.x, self.y = chosen
        self.visited.add(self.pos)
        self.steps_taken += 1

    # -----------------------------------------
    # DETECT CASUALTY
    # -----------------------------------------
    def detect_casualty(self, casualty):
        if self.x == casualty.x and self.y == casualty.y:
            self.has_found = True
            return True

        if self.vision_radius > 0:
            dist = abs(self.x - casualty.x) + abs(self.y - casualty.y)
            if dist <= self.vision_radius:
                self.has_found = True
                return True

        return False
