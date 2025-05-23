#setting up pygame

from operator import index
import pygame
from engine import Game,Ship
from log_helper import set_username
from login import login_screen
from ai_agent import QLearningAgent
import pickle
import sys

username = login_screen()
agent = QLearningAgent(username)
set_username(username)
pygame.init()
pygame.font.init()
pygame.display.set_caption("Battleship AI")
myfont = pygame.font.SysFont("freestanding", 100)
button_font = pygame.font.SysFont("arial", 36)



#display resolution
Display_resolution=pygame.display.Info()
SCREEN_WIDTH,SCREEN_HEIGHT=Display_resolution.current_w, Display_resolution.current_h
SCREEN=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.RESIZABLE)

#Game screen
GAME_AREA_WIDTH=int(SCREEN_WIDTH*0.66)
STAT_AREA_WIDTH=SCREEN_WIDTH - GAME_AREA_WIDTH
GAME_AREA_HEIGHT=SCREEN_HEIGHT

sq_w = GAME_AREA_WIDTH  // 10
sq_h = GAME_AREA_HEIGHT // 10
SQ_SIZE = GAME_AREA_WIDTH // 25

GAME_ORIGIN = (0, 0)
STAT_ORIGIN = (GAME_AREA_WIDTH, 0)

GAME_ORIGIN_X, GAME_ORIGIN_Y = GAME_ORIGIN
GAME_W, GAME_H = GAME_AREA_WIDTH, GAME_AREA_HEIGHT

#global variables

H_MARGIN = SQ_SIZE + 100
V_MARGIN = SQ_SIZE
WIDTH, HEIGHT = SQ_SIZE * 10 * 2 + H_MARGIN, SQ_SIZE * 10 * 2 + V_MARGIN
INDENT =10
LOGIN = False




#colors
GRAY=(60,60,60)
WHITE=(255,250,250)
GREEN=(40,230,40)
RED=(250,50,100)
BLUE=(50,150,200)
ORANGE=(250,140,20)
COLORS = {"U": GRAY, "M": BLUE, "H": ORANGE, "S": RED}

#function to draw a grid
def draw_grid(player, left=0, top=0, search = False):
    for i in range(100):
        x=left + i % 10 * SQ_SIZE
        y=top + i // 10 * SQ_SIZE
        square=pygame.Rect(x,y,SQ_SIZE,SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, square, width = 1)
        if search:
            cx = x + SQ_SIZE // 2
            cy = y + SQ_SIZE // 2
            pygame.draw.circle(SCREEN, COLORS[player.search[i]], (cx, cy),radius = SQ_SIZE//4)

def draw_a_line(left=WIDTH-H_MARGIN//2 + H_MARGIN, top=0):
    x=left-50
    y=top
    pygame.draw.line(SCREEN,WHITE,(x,y),(x,y+SCREEN_WIDTH))




def draw_button(text, rect, color_bg, color_text):
    pygame.draw.rect(SCREEN, color_bg, rect, border_radius=8)
    label = button_font.render(text, True, color_text)
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)


#function to draw ships onto the position girds
def draw_ship(player, left=0, top=0):
    for ship in player.ships:
        x = left + ship.col * SQ_SIZE + INDENT
        y = top + ship.row * SQ_SIZE + INDENT
        if ship.orientation == 'h':
            width = ship.size * SQ_SIZE - 2 * INDENT
            height = SQ_SIZE - 2 * INDENT
        else:
            width = SQ_SIZE - 2 * INDENT
            height = ship.size * SQ_SIZE - 2 * INDENT
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, GREEN, rectangle, border_radius=15)

# function to draw stats on the right side of the screen
def draw_statistics_panel(game):
    panel_x = STAT_ORIGIN[0] + 20
    panel_y = STAT_ORIGIN[1] + 20
    line_spacing = 40
    font = pygame.font.SysFont("arial", 24)

    def render_line(text, y_offset):
        text_surf = font.render(text, True, WHITE)
        SCREEN.blit(text_surf, (panel_x, panel_y + y_offset))

    render_line("📊 Oyun Durumu:", 0)
    render_line("Bitti" if game.over else "Devam ediyor", line_spacing)
    render_line(f"Sıra: {'Oyuncu 1' if game.player1_turn else 'Oyuncu 2'}", line_spacing * 2)
    render_line(f"Toplam Hamle: {game.n_shots}", line_spacing * 3)

    p1_hits = game.player1.search.count("H") + game.player1.search.count("S")
    p1_misses = game.player1.search.count("M")
    p2_hits = game.player2.search.count("H") + game.player2.search.count("S")
    p2_misses = game.player2.search.count("M")

    render_line(f"🎯 Oyuncu 1 - H:{p1_hits} M:{p1_misses}", line_spacing * 5)
    render_line(f"🤖 Oyuncu 2 - H:{p2_hits} M:{p2_misses}", line_spacing * 6)

    if game.n_shots > 0:
        last_player = 2 if game.player1_turn else 1
        render_line(f"Son Hamle: P{last_player}", line_spacing * 8)


#function to split the screen




# BASLANGIC ARAYUZU
def run_menu():
    show_menu = True
    clock = pygame.time.Clock()
    menu_background = pygame.image.load("menu_background.jpg")
    while show_menu:
        SCREEN.blit(menu_background, (0, 0))
        pvp_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 130, 250, 60)
        AI_vs_Player = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 250, 60)
        AI_vs_AI = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 210, 250, 60)
        quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 250, 60)

        draw_button("AI vs AI", AI_vs_AI, GREEN, WHITE)
        draw_button("AI vs Player", AI_vs_Player, BLUE, WHITE)
        draw_button("Quit Game", quit_button, RED, WHITE)
        draw_button("Player vs Player", pvp_button, GREEN, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if AI_vs_Player.collidepoint((mx, my)):
                    return False,True
                elif pvp_button.collidepoint((mx, my)):
                    return True,True
                elif AI_vs_AI.collidepoint((mx, my)):
                    return False,False
                elif quit_button.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

import pygame
import sys
from engine import Game

pygame.init()
pygame.font.init()




def draw_grid_background():
    for i in range(100):
        x = GAME_AREA_WIDTH // 2 - 5 * SQ_SIZE + (i % 10) * SQ_SIZE
        y = SCREEN_HEIGHT // 2 - 5 * SQ_SIZE + (i // 10) * SQ_SIZE
        square = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, square, width=1)




run_menu()
HUMAN1,HUMAN2=run_menu()
game = Game(HUMAN1,HUMAN2)

#pygame loop


# Compute the two shooting‐grid Rects:
P1_RECT = pygame.Rect(0, 0, SQ_SIZE*10, SQ_SIZE*10)
P2_LEFT = (WIDTH - H_MARGIN)//2 + H_MARGIN
P2_TOP  = (HEIGHT - V_MARGIN)//2 + V_MARGIN
P2_RECT = pygame.Rect(P2_LEFT, P2_TOP, SQ_SIZE*10, SQ_SIZE*10)



running = True
pausing = False
while running:
    #track user interaction
    for event in pygame.event.get():
        #user closes the pygame window
        if event.type == pygame.QUIT:
            running = False

        # user clicks on mouse
        if event.type == pygame.MOUSEBUTTONDOWN and not game.over:
           x,y = pygame.mouse.get_pos()
           if game.player1_turn and P1_RECT.collidepoint(x, y):
                           row = (y - P1_RECT.top) // SQ_SIZE
                           col = (x - P1_RECT.left) // SQ_SIZE
                           index = row * 10 + col
                           game.make_move(index)
           elif not game.player1_turn and P2_RECT.collidepoint(x, y):
                           row = (y - P2_RECT.top) // SQ_SIZE
                           col = (x - P2_RECT.left) // SQ_SIZE
                           index = row * 10 + col
                           game.make_move(index)

        #user preses keys on keyboard
        if event.type == pygame.KEYDOWN:
            #escape key to close the animation
            if event.key == pygame.K_ESCAPE:
                running = False
            #space key to pause the animation
            if event.key == pygame.K_SPACE:
                pausing = not pausing

            #return key to restart the game
            if event.key == pygame.K_RETURN:
                game = Game(HUMAN1,HUMAN2)

    #execution
    if not pausing:
        #draw background
        if LOGIN == False:
            username = login_screen()
            print("Oyuncu adı:", username)
            LOGIN = True
        else:

            SCREEN.fill(GRAY)

            # draw search grids
            draw_grid(game.player1, search=True)
            draw_grid(game.player2, search=True, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN,top=(HEIGHT - V_MARGIN) // 2 + V_MARGIN)

            # draw position grids
            draw_grid(game.player1, top=(HEIGHT - V_MARGIN) // 2 + V_MARGIN)
            draw_grid(game.player2, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN)

            draw_a_line()

            # draw ships onto position grids
            draw_ship(game.player1, top=(HEIGHT - V_MARGIN) // 2 + V_MARGIN)
            draw_ship(game.player2, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN)

            # Draw stats panel
            draw_statistics_panel(game)

            # Computer moves
            if not game.over and game.computer_turn:
                # hangi oyuncunun sırasıysa onun search grid’ini al
                current_search = game.player1.search if game.player1_turn else game.player2.search

                # e‑greedy hamleyi seç
                action = agent.choose_action(current_search)
                if action is not None:
                    # güncelleme için eski grid’i sakla
                    prev_search = current_search.copy()
                    # hamleyi uygula
                    game.make_move(action)
                    # ödül hesapla
                    result = current_search[action]  # 'M', 'H' veya 'S'
                    if result == "M":
                        reward = -0.1
                    elif result == "H":
                        reward = +1
                    elif result == "S":
                        reward = +3
                    # yeni grid’i al
                    next_search = current_search
                    # Q‑learning güncellemesi
                    agent.update_q(prev_search, action, reward, next_search)


            # game over message
            if game.over:
                text = "Player" + str(game.result) + " wins!"
                textbox = myfont.render(text, False, GRAY, WHITE)
                SCREEN.blit(textbox, (WIDTH // 2 - 240, HEIGHT // 2 - 50))
        # update screen
        pygame.time.wait(100)
        pygame.display.flip()











