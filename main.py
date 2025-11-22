import pygame
import sys

from core.simulation import Simulation
from renderer.renderer import Renderer
from core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 10

def main():
    pygame.init()
    pygame.display.set_caption("Search & Rescue MAS")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    sim = Simulation()
    renderer = Renderer(screen, sim)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.toggle()
                elif event.key == pygame.K_r:
                    sim.reset()
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        sim.update()
        renderer.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
