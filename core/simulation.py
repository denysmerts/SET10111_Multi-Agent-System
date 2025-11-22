import time
from core.environment import Environment
from agents.searcher import Searcher
from agents.casualty import Casualty
from agents.drone import Drone, DRONE_VISION_RADIUS
from core.constants import GRID_WIDTH, GRID_HEIGHT


NUM_SEARCHERS = 3


class Simulation:
    def __init__(self):

        # ---------------------------------------------
        # ENVIRONMENT
        # ---------------------------------------------
        self.env = Environment(GRID_WIDTH, GRID_HEIGHT)

        # ---------------------------------------------
        # CASUALTY
        # ---------------------------------------------
        c = self.env.random_free_cell()
        self.casualty = Casualty(c.x, c.y)

        # ---------------------------------------------
        # SEARCHERS
        # ---------------------------------------------
        self.searchers = []
        for i in range(NUM_SEARCHERS):
            while True:
                s = self.env.random_free_cell()
                if (s.x, s.y) != self.casualty.pos:
                    break
            self.searchers.append(Searcher(i + 1, s.x, s.y))

        # ---------------------------------------------
        # SHARED KNOWLEDGE MAP (COOPERATIVE SEARCH)
        # ---------------------------------------------
        self.shared_visit_count = {}   # (x,y) → visits by ANY searcher

        # Attach to each searcher
        for s in self.searchers:
            s.shared_visit_count = self.shared_visit_count

        # ---------------------------------------------
        # DRONE — ensure it spawns OUTSIDE vision of casualty
        # ---------------------------------------------
        while True:
            d = self.env.random_free_cell()
            dist = abs(d.x - self.casualty.x) + abs(d.y - self.casualty.y)
            if dist > DRONE_VISION_RADIUS:
                break

        self.drone = Drone(id_=99, x=d.x, y=d.y)

        # ---------------------------------------------
        # SIMULATION STATE
        # ---------------------------------------------
        self.running = False
        self.start_time = None
        self.step_count = 0
        self.time_to_find = None
        self.found_by = None

    # -------------------------------------------------------------
    # PUBLIC CONTROL METHODS
    # -------------------------------------------------------------
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
            s.visit_count = {s.pos: 1}
            s.last_pos = None
            s.mode = "search"
            s.target = None

        self.shared_visit_count.clear()

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

    # -------------------------------------------------------------
    # UPDATE — main simulation tick
    # -------------------------------------------------------------
    def update(self):
        if not self.running:
            return

        self.step_count += 1

        # ---------------------------------------------------------
        # SEARCHERS UPDATE
        # ---------------------------------------------------------
        for s in self.searchers:
            s.step(self.env)

            # LOCAL DETECTION (searcher physically reaches casualty)
            if self.time_to_find is None:
                if s.detect_casualty(self.casualty):
                    self.time_to_find = time.time() - self.start_time
                    self.found_by = s.id

        # ---------------------------------------------------------
        # DRONE UPDATE
        # ---------------------------------------------------------
        self.drone.step(self.env)

        # DRONE DETECTION
        if self.time_to_find is None:
            if self.drone.detect_casualty(self.casualty):
                self.time_to_find = time.time() - self.start_time
                self.found_by = self.drone.id

                # Drone broadcasts casualty location to ALL searchers
                for s in self.searchers:
                    s.mode = "rescue"
                    s.target = (self.casualty.x, self.casualty.y)

    # -------------------------------------------------------------
    @property
    def elapsed_time(self):
        if self.start_time is None:
            return 0.0
        if self.time_to_find is not None:
            return self.time_to_find
        return time.time() - self.start_time
