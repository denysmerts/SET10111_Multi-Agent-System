import random
from .agent import Agent


class Searcher(Agent):
    def __init__(self, id_, x, y, vision_radius=0):
        super().__init__(id_, x, y)

        # Behaviour
        self.vision_radius = vision_radius
        self.has_found = False
        self.at_casualty = False
        self.arrival_time = None
        self.steps_taken = 0

        # Local memory
        self.visited = {self.pos}
        self.visit_count = {self.pos: 1}
        self.last_pos = None

        # Shared memory (set later by Simulation)
        self.shared_visit_count = None

        # Modes
        self.mode = "search"     
        self.target = None       

    # Neighbour cells

    def neighbours(self, env):
        candidates = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1),
        ]
        return [(x, y) for (x, y) in candidates if env.is_free(x, y)]

    # Main Step Function

    def step(self, env):
        if self.at_casualty:
            return

     
        # RESCUE MODE: move toward the known casualty location
        if self.mode == "rescue" and self.target:
            tx, ty = self.target

            dx = tx - self.x
            dy = ty - self.y

            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0

            new_x = self.x + move_x
            new_y = self.y + move_y

            if env.is_free(new_x, new_y):
                self._apply_move(new_x, new_y)
                return

            # fallback
            options = self.neighbours(env)
            if options:
                new_x, new_y = random.choice(options)
                self._apply_move(new_x, new_y)
            return

       
        # SEARCH MODE: cooperative frontier-based exploration

        options = self.neighbours(env)
        if not options:
            return

        # Initialise shared counters
        for pos in options:
            if pos not in self.shared_visit_count:
                self.shared_visit_count[pos] = 0

        # Prefer unvisited cells globally
        unvisited = [pos for pos in options if self.shared_visit_count[pos] == 0]

        if unvisited:
            chosen = random.choice(unvisited)
        else:
            # Take the least globally visited option
            min_visits = min(self.shared_visit_count[pos] for pos in options)
            best_options = [pos for pos in options if self.shared_visit_count[pos] == min_visits]
            chosen = random.choice(best_options)

        # Avoid oscillating back and forth
        if self.last_pos and chosen == self.last_pos and len(options) > 1:
            alternatives = [p for p in options if p != self.last_pos]
            chosen = random.choice(alternatives)

        new_x, new_y = chosen
        self._apply_move(new_x, new_y)

   
    # MOVE APPLY HELPER

    def _apply_move(self, new_x, new_y):
        self.last_pos = (self.x, self.y)
        self.x, self.y = new_x, new_y

        self.steps_taken += 1

        # Local memory
        self.visited.add(self.pos)
        self.visit_count[self.pos] = self.visit_count.get(self.pos, 0) + 1

        # Shared memory
        self.shared_visit_count[self.pos] = self.shared_visit_count.get(self.pos, 0) + 1

   
    # Detect casualty

    def detect_casualty(self, casualty, t):
        if (self.x, self.y) == (casualty.x, casualty.y):
            if not self.at_casualty:
                self.at_casualty = True
                self.arrival_time = t
                self.has_found = True
            return True
        return False
