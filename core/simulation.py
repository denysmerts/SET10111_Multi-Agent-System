import time
from core.environment import Environment
from agents.searcher import Searcher
from agents.casualty import Casualty
from agents.drone import Drone
from agents.drone import DRONE_VISION_RADIUS

from core.constants import GRID_WIDTH, GRID_HEIGHT


NUM_SEARCHERS = 3


class Simulation:
    def __init__(self):
        # Create environment
        self.env = Environment(GRID_WIDTH, GRID_HEIGHT)

        # Spawn casualty
        c = self.env.random_free_cell()
        self.casualty = Casualty(c.x, c.y)

        # Spawn searchers
        self.searchers = []
        for i in range(NUM_SEARCHERS):
            while True:
                s = self.env.random_free_cell()
                if (s.x, s.y) != self.casualty.pos:
                    break
            self.searchers.append(Searcher(i + 1, s.x, s.y))

        # Spawn drone far enough from casualty
        while True:
            d = self.env.random_free_cell()
            dist = abs(d.x - self.casualty.x) + abs(d.y - self.casualty.y)
            if dist > DRONE_VISION_RADIUS:
                break

        self.drone = Drone(id_=99, x=d.x, y=d.y)

        # Simulation state
        self.running = False
        self.step_count = 0
        self.start_time = None
        self.time_to_find = None
        self.found_by = None

    # ---------------------------------------------
    # CONTROL
    # ---------------------------------------------
    def reset(self):
        self.__init__()

    def start(self):
        self.running = True
        self.step_count = 0
        self.start_time = time.time()
        self.time_to_find = None
        self.found_by = None

        # Reset agents
        for s in self.searchers:
            s.has_found = False
            s.steps_taken = 0
            s.visited = {s.pos}
            s.last_pos = None
            s.mode = "search"
            s.target = None

        self.drone.has_found = False
        self.drone.steps_taken = 0

    def toggle(self):
        if not self.running:
            if self.start_time is None:
                self.start()
            else:
                self.running = True
        else:
            self.running = False

    # ---------------------------------------------
    # MAIN SIMULATION UPDATE
    # ---------------------------------------------
    def update(self):
        if not self.running:
            return

        self.step_count += 1

        # --------------------------
        # Searchers update
        # --------------------------
        for s in self.searchers:
            s.step(self.env)

            if self.time_to_find is None:
                if s.detect_casualty(self.casualty):
                    self.found_by = s.id
                    self.time_to_find = time.time() - self.start_time

        # --------------------------
        # Drone update
        # --------------------------
        self.drone.step(self.env)

        if self.time_to_find is None:
            if self.drone.detect_casualty(self.casualty):
                self.found_by = self.drone.id
                self.time_to_find = time.time() - self.start_time

                # Drone communicates target to all searchers
                for s in self.searchers:
                    s.mode = "rescue"
                    s.target = (self.casualty.x, self.casualty.y)

    # ---------------------------------------------
    @property
    def elapsed_time(self):
        if self.start_time is None:
            return 0.0
        if self.time_to_find is not None:
            return self.time_to_find
        return time.time() - self.start_time
