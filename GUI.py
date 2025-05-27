# GUI.py
from operator import index
import pygame
from engine import Game, Ship
from log_helper import set_username
from login import login_screen
from ai_agent import QLearningAgent
import pickle
import sys
from Log_Analiz import load_logs, plot_average_turns, plot_heatmap, plot_ship_placement
import os

username = login_screen()
agent = QLearningAgent(username)
set_username(username)
pygame.init()
pygame.font.init()
pygame.display.set_caption("Battleship AI")
myfont = pygame.font.SysFont("freestanding", 100)
button_font = pygame.font.SysFont("arial", 24)

Display_resolution = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = Display_resolution.current_w, Display_resolution.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

GAME_AREA_WIDTH = int(SCREEN_WIDTH * 0.66)
STAT_AREA_WIDTH = SCREEN_WIDTH - GAME_AREA_WIDTH
GAME_AREA_HEIGHT = SCREEN_HEIGHT

sq_w = GAME_AREA_WIDTH // 10
sq_h = GAME_AREA_HEIGHT // 10
SQ_SIZE = GAME_AREA_WIDTH // 25

GAME_ORIGIN = (0, 0)
STAT_ORIGIN = (GAME_AREA_WIDTH, 0)

H_MARGIN = SQ_SIZE + 100
V_MARGIN = SQ_SIZE
WIDTH, HEIGHT = SQ_SIZE * 10 * 2 + H_MARGIN, SQ_SIZE * 10 * 2 + V_MARGIN
INDENT = 10
LOGIN = False

GRAY = (60, 60, 60)
WHITE = (255, 250, 250)
GREEN = (40, 230, 40)
RED = (250, 50, 100)
BLUE = (50, 150, 200)
ORANGE = (250, 140, 20)
COLORS = {"U": GRAY, "M": BLUE, "H": ORANGE, "S": RED}

ANALYSIS_BUTTONS = []
GRAPH_IMAGE = None

def draw_grid(player, left=0, top=0, search=False):
    for i in range(100):
        x = left + i % 10 * SQ_SIZE
        y = top + i // 10 * SQ_SIZE
        square = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, square, width=1)
        if search:
            cx = x + SQ_SIZE // 2
            cy = y + SQ_SIZE // 2
            pygame.draw.circle(SCREEN, COLORS[player.search[i]], (cx, cy), radius=SQ_SIZE // 4)

def draw_a_line(left=WIDTH - H_MARGIN // 2 + H_MARGIN, top=0):
    x = left - 50
    y = top
    pygame.draw.line(SCREEN, WHITE, (x, y), (x, y + SCREEN_WIDTH))

def draw_button(text, rect, color_bg, color_text):
    pygame.draw.rect(SCREEN, color_bg, rect, border_radius=8)
    label = button_font.render(text, True, color_text)
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)

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

def draw_statistics_panel(game):
    global GRAPH_IMAGE
    panel_x = STAT_ORIGIN[0] + 20
    panel_y = STAT_ORIGIN[1] + 20
    font = pygame.font.SysFont("arial", 24)
    line_spacing = 30

    def render_line(text, y_offset):
        text_surf = font.render(text, True, WHITE)
        SCREEN.blit(text_surf, (panel_x, panel_y + y_offset))

    render_line("\U0001F4CA Oyun Durumu:", 0)
    render_line("Bitti" if game.over else "Devam ediyor", line_spacing)
    render_line(f"Sıra: {'Oyuncu 1' if game.player1_turn else 'Oyuncu 2'}", line_spacing * 2)
    render_line(f"Toplam Hamle: {game.n_shots}", line_spacing * 3)

    p1_hits = game.player1.search.count("H") + game.player1.search.count("S")
    p1_misses = game.player1.search.count("M")
    p2_hits = game.player2.search.count("H") + game.player2.search.count("S")
    p2_misses = game.player2.search.count("M")

    render_line(f"Oyuncu 1 - Hit: {p1_hits}, Miss: {p1_misses}", line_spacing * 4)
    render_line(f"Oyuncu 2 - Hit: {p2_hits}, Miss: {p2_misses}", line_spacing * 5)

    if game.n_shots > 0:
        last_player = 2 if game.player1_turn else 1
        render_line(f"Son Hamle: Oyuncu {last_player}", line_spacing * 6)

    ANALYSIS_BUTTONS.clear()
    labels = [
        ("Atış Sayısı", "plot_avg_turns.png"),
        ("Heatmap Q-table", "plot_qtable_heatmap.png"),
        ("Heatmap allships", "plot_heatmap_ships.png")
    ]
    b_y = panel_y + line_spacing * 7
    button_width, button_height = 160, 40
    spacing = 10

    for i, (text, _) in enumerate(labels):
        rect = pygame.Rect(panel_x + i * (button_width + spacing), b_y, button_width, button_height)
        draw_button(text, rect, BLUE, WHITE)
        ANALYSIS_BUTTONS.append((rect, text))

    if GRAPH_IMAGE:
        try:
            img = pygame.image.load(GRAPH_IMAGE)
            img = pygame.transform.scale(img, (STAT_AREA_WIDTH - 40, STAT_AREA_WIDTH - 40))
            SCREEN.blit(img, (panel_x, b_y + button_height + 20))
        except:
            pass


# GUI.py'ye yeni fonksiyonlar ekleyin
def draw_ship_placement_screen(ships, selected_ship=None):
    """Gemileri yerleştirme ekranını çizer"""
    SCREEN.fill(GRAY)

    # Oyun alanı (10x10 grid)
    for i in range(100):
        x = i % 10 * SQ_SIZE
        y = i // 10 * SQ_SIZE
        rect = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, rect, 1)

    # Yerleştirilmiş gemileri çiz
    for ship in ships:
        if ship.placed:
            draw_single_ship(ship)

    # Seçili gemiyi çiz (fare ile sürüklenen)
    if selected_ship:
        draw_single_ship(selected_ship)

    # Start butonu (tüm gemiler yerleşmişse)
    if all(ship.placed for ship in ships):
        start_btn = pygame.Rect(GAME_AREA_WIDTH // 2 - 50, GAME_AREA_HEIGHT - 70, 100, 50)
        draw_button("START", start_btn, GREEN, WHITE)
        return start_btn
    return None


def draw_single_ship(ship):
    """Tek bir gemi çizer"""
    x = ship.col * SQ_SIZE + INDENT
    y = ship.row * SQ_SIZE + INDENT
    if ship.orientation == 'h':
        width = ship.size * SQ_SIZE - 2 * INDENT
        height = SQ_SIZE - 2 * INDENT
    else:
        width = SQ_SIZE - 2 * INDENT
        height = ship.size * SQ_SIZE - 2 * INDENT
    pygame.draw.rect(SCREEN, GREEN, (x, y, width, height), border_radius=10)


def ship_placement_phase():
    """Gemileri yerleştirme aşamasını yönetir"""
    ships = [
        Ship(size=5, row=0, col=0, orientation='h', placed=False),
        Ship(size=4, row=2, col=0, orientation='h', placed=False),
        Ship(size=3, row=4, col=0, orientation='h', placed=False),
        Ship(size=3, row=6, col=0, orientation='h', placed=False),
        Ship(size=2, row=8, col=0, orientation='h', placed=False)
    ]

    selected_ship = None
    dragging = False
    start_btn = None

    while True:
        start_btn = draw_ship_placement_screen(ships, selected_ship)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Start butonuna basıldı mı?
                if start_btn and start_btn.collidepoint((x, y)):
                    return [s for s in ships if s.placed]

                # Gemi seçimi
                for ship in reversed(ships):  # En büyük gemiden başla
                    if not ship.placed and ship.collidepoint(x // SQ_SIZE, y // SQ_SIZE):
                        selected_ship = ship
                        dragging = True
                        break

            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                if selected_ship:
                    # Geçerli bir pozisyona yerleştirildi mi kontrol et
                    if is_valid_position(selected_ship, ships):
                        selected_ship.placed = True
                    selected_ship = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                if selected_ship:
                    # Gemiyi fareyle sürükle
                    selected_ship.col = max(0, min(9, event.pos[0] // SQ_SIZE))
                    selected_ship.row = max(0, min(9, event.pos[1] // SQ_SIZE))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R tuşuyla yön değiştir
                    if selected_ship:
                        selected_ship.orientation = 'v' if selected_ship.orientation == 'h' else 'h'

        pygame.display.flip()
        pygame.time.delay(30)


def is_valid_position(ship, all_ships):
    """Geminin geçerli bir pozisyonda olup olmadığını kontrol eder"""
    # Sınır kontrolü
    if ship.orientation == 'h' and ship.col + ship.size > 10:
        return False
    elif ship.orientation == 'v' and ship.row + ship.size > 10:
        return False

    # Çarpışma kontrolü
    for other in all_ships:
        if other != ship and other.placed:
            if check_collision(ship, other):
                return False
    return True


def check_collision(ship1, ship2):
    """İki gemi arasında çarpışma olup olmadığını kontrol eder"""
    # Basit dikdörtgen çarpışma kontrolü
    rect1 = pygame.Rect(ship1.col, ship1.row,
                        ship1.size if ship1.orientation == 'h' else 1,
                        ship1.size if ship1.orientation == 'v' else 1)
    rect2 = pygame.Rect(ship2.col, ship2.row,
                        ship2.size if ship2.orientation == 'h' else 1,
                        ship2.size if ship2.orientation == 'v' else 1)
    return rect1.colliderect(rect2)



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
                    return False, True
                elif pvp_button.collidepoint((mx, my)):
                    return True, True
                elif AI_vs_AI.collidepoint((mx, my)):
                    return False, False
                elif quit_button.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

HUMAN1, HUMAN2 = run_menu()
game = Game(HUMAN1, HUMAN2)

P1_RECT = pygame.Rect(0, 0, SQ_SIZE * 10, SQ_SIZE * 10)
P2_LEFT = (WIDTH - H_MARGIN) // 2 + H_MARGIN
P2_TOP = (HEIGHT - V_MARGIN) // 2 + V_MARGIN
P2_RECT = pygame.Rect(P2_LEFT, P2_TOP, SQ_SIZE * 10, SQ_SIZE * 10)

running = True
pausing = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
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

            for rect, label in ANALYSIS_BUTTONS:
                if rect.collidepoint(x, y):
                    df_moves, df_ships = load_logs()
                    if label == "Atış Sayısı":
                        plot_average_turns(df_moves)
                        GRAPH_IMAGE = "plot_avg_turns.png"
                    elif label == "Heatmap allships":
                        plot_ship_placement(df_ships, save_path="plot_heatmap_ships.png")
                        GRAPH_IMAGE = "plot_heatmap_ships.png"



                    elif label == "Heatmap Q-table":

                        # Eski heatmap'i sil

                        heatmap_path = "plot_qtable_heatmap.png"

                        if os.path.exists(heatmap_path):
                            os.remove(heatmap_path)

                        # Ayrı oyun dosyalarından öğren

                        agent.learn_from_logs()

                        # Yeni heatmap oluştur

                        agent.plot_aggregated_qtable()

                        GRAPH_IMAGE = heatmap_path

                        pygame.display.flip()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                pausing = not pausing
            if event.key == pygame.K_RETURN:
                game = Game(HUMAN1, HUMAN2)

    if not pausing:
        if not LOGIN:
            username = login_screen()
            LOGIN = True
        else:
            SCREEN.fill(GRAY)
            draw_grid(game.player1, search=True)
            draw_grid(game.player2, search=True, left=P2_LEFT, top=P2_TOP)
            draw_grid(game.player1, top=P2_TOP)
            draw_grid(game.player2, left=P2_LEFT)
            draw_a_line()
            draw_ship(game.player1, top=P2_TOP)
            draw_ship(game.player2, left=P2_LEFT)
            draw_statistics_panel(game)

            if not game.over and game.computer_turn:
                current_search = game.player1.search if game.player1_turn else game.player2.search
                action = agent.choose_action(current_search)
                if action is not None:
                    prev_search = current_search.copy()
                    game.make_move(action)
                    result = current_search[action]
                    reward = -0.1 if result == "M" else 1 if result == "H" else 3
                    next_search = current_search
                    agent.update_q(prev_search, action, reward, next_search)

            if game.over:
                text = "Player" + str(game.result) + " wins!"
                textbox = myfont.render(text, False, GRAY, WHITE)
                SCREEN.blit(textbox, (WIDTH // 2 - 240, HEIGHT // 2 - 50))

        pygame.time.wait(100)
        pygame.display.flip()
