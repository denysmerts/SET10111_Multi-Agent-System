import pygame
import os
from core.constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, SIDE_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT
from agents.searcher import Searcher
from agents.casualty import Casualty
from agents.drone import Drone

# LOAD AGENT IMAGES

ASSETS_PATH = "assets"

DRONE_IMAGE = pygame.image.load(os.path.join(ASSETS_PATH, "drone.png"))
DRONE_IMAGE = pygame.transform.smoothscale(DRONE_IMAGE, (CELL_SIZE, CELL_SIZE))

SEARCHER_IMAGE = pygame.image.load(os.path.join(ASSETS_PATH, "rescuer.png"))
SEARCHER_IMAGE = pygame.transform.smoothscale(SEARCHER_IMAGE, (CELL_SIZE, CELL_SIZE))

CASUALTY_IMAGE = pygame.image.load(os.path.join(ASSETS_PATH, "casualty.png"))
CASUALTY_IMAGE = pygame.transform.smoothscale(CASUALTY_IMAGE, (CELL_SIZE, CELL_SIZE))


# COLORS 
COLOR_BG = (10, 10, 20)
COLOR_GRID = (30, 30, 40)
COLOR_SEARCHER = (56, 189, 248)
COLOR_SEARCHER_FOUND = (34, 197, 94)
COLOR_CASUALTY = (248, 113, 113)
COLOR_OBSTACLE = (71, 85, 105)
COLOR_PANEL_BG = (15, 23, 42)
COLOR_TEXT = (226, 232, 240)
COLOR_HIGHLIGHT = (129, 140, 248)
COLOR_BORDER = (55, 65, 81)


class Renderer:
    def __init__(self, screen: pygame.Surface, sim):
        self.screen = screen
        self.sim = sim
        pygame.font.init()
        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_med = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_big = pygame.font.SysFont("consolas", 24, bold=True)

  
    # GRID + OBSTACLES
  
    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_obstacles(self):
        for (x, y) in self.sim.env.obstacles:
            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_OBSTACLE, rect)

   
    # DRAW AGENTS 

    def draw_agents(self):
        # Casualty image
        cx, cy = self.sim.casualty.pos
        self.screen.blit(CASUALTY_IMAGE, (cx * CELL_SIZE, cy * CELL_SIZE))

        # Searchers images
        for s in self.sim.searchers:
            sx, sy = s.pos
            self.screen.blit(SEARCHER_IMAGE, (sx * CELL_SIZE, sy * CELL_SIZE))

        # Drone image
        dx, dy = self.sim.drone.pos
        self.screen.blit(DRONE_IMAGE, (dx * CELL_SIZE, dy * CELL_SIZE))

   
    # SIDE PANEL
  
    def draw_panel(self):
        panel_rect = pygame.Rect(
            GRID_WIDTH * CELL_SIZE,
            0,
            SIDE_PANEL_WIDTH,
            WINDOW_HEIGHT
        )
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, panel_rect, 1)

        x0 = GRID_WIDTH * CELL_SIZE + 16
        y = 16

        # Title
        title = self.font_big.render("Search & Rescue MAS", True, COLOR_TEXT)
        self.screen.blit(title, (x0, y))
        y += 32


        # Status
        status = "RUNNING" if self.sim.running else "PAUSED"
        status_color = COLOR_HIGHLIGHT if self.sim.running else COLOR_TEXT
        status_text = self.font_med.render(f"Status: {status}", True, status_color)
        self.screen.blit(status_text, (x0, y))
        y += 28

        

        self.screen.blit(self.font_small.render(f"Time: {self.sim.elapsed_time:.1f}s", True, COLOR_TEXT), (x0, y))
        y += 22

        # Found info
        if self.sim.time_to_find is not None:
            self.screen.blit(self.font_small.render(
                f"Casualty found by: {self.sim.found_by}", True, COLOR_HIGHLIGHT), (x0, y))
            y += 22

            self.screen.blit(self.font_small.render(
                f"in {self.sim.time_to_find:.1f}s", True, COLOR_HIGHLIGHT), (x0, y))
            y += 26

            # Arrival times per searcher
            arrivals = [s for s in self.sim.searchers if s.arrival_time is not None]
            if arrivals:
                arrivals.sort(key=lambda a: a.arrival_time)
                self.screen.blit(self.font_small.render(
                    "Arrival times:", True, COLOR_HIGHLIGHT), (x0, y))
                y += 22

                for i, s in enumerate(arrivals, start=1):
                    if i == 1:
                        suffix = "st"
                    elif i == 2:
                        suffix = "nd"
                    elif i == 3:
                        suffix = "rd"
                    else:
                        suffix = "th"

                    line = f"{i}{suffix}: S{s.id} at {s.arrival_time:.1f}s"
                    self.screen.blit(self.font_small.render(line, True, COLOR_TEXT), (x0, y))
                    y += 20

                if self.sim.all_rescued_time is not None:
                    msg = f"All rescuers reached casualty at {self.sim.all_rescued_time:.1f}s"
                    self.screen.blit(self.font_small.render(msg, True, COLOR_HIGHLIGHT), (x0, y))
                    y += 24

        else:
            self.screen.blit(self.font_small.render("Casualty not yet found", True, COLOR_TEXT), (x0, y))
            y += 26

        # Divider
        pygame.draw.line(self.screen, COLOR_BORDER,
                         (GRID_WIDTH * CELL_SIZE + 12, y),
                         (WINDOW_WIDTH - 16, y), 1)
        y += 16

        # Searcher list
        header = self.font_med.render("Searchers", True, COLOR_TEXT)
        self.screen.blit(header, (x0, y))
        y += 28

        for s in self.sim.searchers:
            self.screen.blit(self.font_small.render(
                f"S{s.id}: mode={s.mode}, steps={s.steps_taken}", True, COLOR_TEXT), (x0, y))
            y += 20

        # Drone info
        y += 6
        self.screen.blit(self.font_small.render(
            f"Drone: steps={self.sim.drone.steps_taken}",
            True,
            COLOR_HIGHLIGHT
        ), (x0, y))
        y += 26

        # Divider
        pygame.draw.line(self.screen, COLOR_BORDER,
                         (GRID_WIDTH * CELL_SIZE + 12, y),
                         (WINDOW_WIDTH - 16, y), 1)
        y += 16

        # Controls
        ctrl = self.font_med.render("Controls", True, COLOR_TEXT)
        self.screen.blit(ctrl, (x0, y))
        y += 26

        controls_list = [
            "SPACE - Start/Pause",
            "R     - Reset",
            "ESC/Q - Quit"
        ]

        for line in controls_list:
            self.screen.blit(self.font_small.render(line, True, COLOR_TEXT), (x0, y))
            y += 20

    
    # MASTER DRAW FUNCTION
    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_grid()
        self.draw_obstacles()
        self.draw_agents()
        self.draw_panel()
