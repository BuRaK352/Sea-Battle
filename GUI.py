#setting up pygame

import pygame
from engine import Player

pygame.init()
pygame.display.set_caption("Battleship AI")

#global variables
SQ_SIZE = 30
H_MARGIN = SQ_SIZE * 4
V_MARGIN = SQ_SIZE
WIDTH, HEIGHT = SQ_SIZE * 10 * 2 + H_MARGIN, SQ_SIZE * 10 * 2 + V_MARGIN

SCREEN=pygame.display.set_mode((WIDTH,HEIGHT))

#colors
GRAY=(60,60,60)
WHITE=(255,250,250)
GREEN=(40,230,40)

#function to draw a grid
def draw_grid(left=0, top=0):
    for i in range(100):
        x=left + i % 10 * SQ_SIZE
        y=top + i // 10 * SQ_SIZE
        square=pygame.Rect(x,y,SQ_SIZE,SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, square, width = 1)

#function to draw ships onto the position girds
def draw_ship(player, left=0, top=0):
    for ship in player.ships:
        x = left + ship.col * SQ_SIZE
        y = top + ship.row * SQ_SIZE
        if ship.orientation == 'horizontal':
            width = ship.size * SQ_SIZE
            height = SQ_SIZE
        else:
            width = SQ_SIZE
            height = ship.size * SQ_SIZE
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, GREEN, rectangle)



#function to split the screen
def draw_a_line(left=1920/3, top=0):
    x=left
    y=top


player = Player()




#pygame loop
animating = True
pausing = False
while animating:
    #track user interaction
    for event in pygame.event.get():
        #user closes the pygame window
        if event.type == pygame.QUIT:
            animating = False
        #user preses keys on keyboard
        if event.type == pygame.KEYDOWN:
            #escape key to close the animation
            if event.key == pygame.K_ESCAPE:
                animating = False
            #space key to pause the animation
            if event.key == pygame.K_SPACE:
                pausing = not pausing

    #execution
    if not pausing:
        #draw background
        SCREEN.fill(GRAY)
        #draw search grids
        draw_grid()
        draw_grid(left=(WIDTH-H_MARGIN)//2 + H_MARGIN, top=(HEIGHT-V_MARGIN)//2 + V_MARGIN)

        #draw position grids
        draw_grid(top=(HEIGHT-V_MARGIN)//2 + V_MARGIN)
        draw_grid(left=(WIDTH-H_MARGIN)//2 + H_MARGIN)

        #draw ships onto position grids
        draw_ship(player)
        #update screen
        pygame.display.flip()

