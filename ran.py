import pygame
from matplotlib.patches import Rectangle

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    elif event.type = KE


    pygame.draw.rect(screen, (255,255,255), (100, 100, 100,100))
    pygame.display.flip()






