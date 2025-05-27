# --- Temel Ayarlar ve Global Değişkenler ---
placed_ships = []
remaining_ships = [5, 4, 3, 3, 2,]
placing_orientation = "h"

# --- Gemi Yerleştirme Fonksiyonları ---
def draw_ship_preview(row, col, size, orientation, color=GREEN):
    for i in range(size):
        dx = i if orientation == "h" else 0
        dy = i if orientation == "v" else 0
        x = GAME_AREA_WIDTH // 2 - 5 * SQ_SIZE + (col + dx) * SQ_SIZE + INDENT
        y = SCREEN_HEIGHT // 2 - 5 * SQ_SIZE + (row + dy) * SQ_SIZE + INDENT
        w = SQ_SIZE - 2 * INDENT
        h = SQ_SIZE - 2 * INDENT
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(SCREEN, color, rect, border_radius=6)

def is_valid_placement(row, col, size, orientation):
    for i in range(size):
        dx = i if orientation == "h" else 0
        dy = i if orientation == "v" else 0
        r = row + dy
        c = col + dx
        if r >= 10 or c >= 10:
            return False
        index = r * 10 + c
        for ship in placed_ships:
            if index in ship["cells"]:
                return False
    return True

def add_ship(row, col, size, orientation):
    cells = []
    for i in range(size):
        dx = i if orientation == "h" else 0
        dy = i if orientation == "v" else 0
        r = row + dy
        c = col + dx
        cells.append(r * 10 + c)
    placed_ships.append({"size": size, "cells": cells})


from engine import Ship  # yukarıya eklendiğinden emin ol



def draw_ship_list():
    font = pygame.font.SysFont("arial", 24)
    x, y = STAT_ORIGIN[0] + 20, 200
    line_height = 35
    SCREEN.blit(font.render("Kalan Gemiler:", True, WHITE), (x, y - 40))
    counted = {}
    for size in remaining_ships:
        counted[size] = counted.get(size, 0) + 1
    for i, (size, count) in enumerate(sorted(counted.items(), reverse=True)):
        SCREEN.blit(font.render(f"{size} birimlik gemi x{count}", True, WHITE), (x, y + i * line_height))

# --- Gemi Yerleştirme Ana Fonksiyonu ---
def run_ship_placement():
    global placing_orientation
    clock = pygame.time.Clock()
    placing = True

    while placing:
        SCREEN.fill(GRAY)
        draw_grid_background()
        draw_ship_list()

        mx, my = pygame.mouse.get_pos()
        grid_x = GAME_AREA_WIDTH // 2 - 5 * SQ_SIZE
        grid_y = SCREEN_HEIGHT // 2 - 5 * SQ_SIZE
        col = (mx - grid_x) // SQ_SIZE
        row = (my - grid_y) // SQ_SIZE

        # Geçerli konumda hover gemi göster
        if 0 <= row < 10 and 0 <= col < 10 and remaining_ships:
            size = remaining_ships[0]
            if is_valid_placement(row, col, size, placing_orientation):
                draw_ship_preview(row, col, size, placing_orientation, ORANGE)

        # Yerleştirilen gemileri çiz
        for ship in placed_ships:
            for idx in ship["cells"]:
                r, c = idx // 10, idx % 10
                draw_ship_preview(r, c, 1, "h", GREEN)

        # Event kontrolü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    placing_orientation = "v" if placing_orientation == "h" else "h"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= row < 10 and 0 <= col < 10 and remaining_ships:
                    size = remaining_ships[0]
                    if is_valid_placement(row, col, size, placing_orientation):
                        add_ship(row, col, size, placing_orientation)
                        remaining_ships.pop(0)

        # Tüm gemiler yerleştiyse start butonu göster
        if not remaining_ships:
            start_btn = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100, 200, 60)
            draw_button("Start", start_btn, BLUE, WHITE)
            if pygame.mouse.get_pressed()[0] and start_btn.collidepoint(pygame.mouse.get_pos()):
                placing = False

        pygame.display.flip()
        clock.tick(60)





#BURADAKILER ENGINE.PY DOSYASININ ICINDEKILERLE ILGILI
import random
from log_helper import create_log_data, add_move, finalize_log


class Ship:
    def __init__(self, size, row=None, col=None, orientation=None):
        self.size = size
        self.orientation = orientation
        self.row = row
        self.col = col
        self.indexes = []

        if self.row is not None and self.col is not None and self.orientation is not None:
            self.indexes = self.compute_indexes()

    def compute_indexes(self):
        if self.orientation == "h":
            if self.col + self.size > 10:
                return []
            return [self.row * 10 + self.col + i for i in range(self.size)]
        else:
            if self.row + self.size > 10:
                return []
            return [(self.row + i) * 10 + self.col for i in range(self.size)]


def place_random_ship(board, size):
    while True:
        orientation = random.choice(["h", "v"])
        row = random.randint(0, 9)
        col = random.randint(0, 9)

        ship = Ship(size, row, col, orientation)
        if not ship.indexes:
            continue
        if all(board[i] == 0 for i in ship.indexes):
            for i in ship.indexes:
                board[i] = 1
            return ship


def setup_ai_ships():
    ai_board = [0] * 100
    ai_ships = []
    for size in [5, 4, 3, 3, 2]:
        ship = place_random_ship(ai_board, size)
        ai_ships.append(ship)
    return ai_ships


class Player:
    def __init__(self, human=False):
        self.human = human
        self.ships = []
        self.search = ["U"] * 100
        self.indexes = []

    def update_indexes(self):
        self.indexes = [i for ship in self.ships for i in ship.indexes]


    # Yeni fonksiyon: Manuel olarak gemi yerleştirme (GUI'den çağrılacak)
    def place_ship_manually(self, size, row, col, orientation):
        ship = Ship(size, row, col, orientation)
        if not ship.indexes:
            return False  # Geçersiz yerleşim (tahta dışı)

        # Diğer gemilerle çakışma kontrolü
        for existing_ship in self.ships:
            if set(ship.indexes) & set(existing_ship.indexes):
                return False

        self.ships.append(ship)
        self.update_indexes()
        return True


class Game:
    def __init__(self, human1=False, human2=False):
        self.human1 = human1
        self.human2 = human2

        self.player1 = Player(human1)
        self.player2 = Player(human2)

        # AI oyuncu ise gemileri otomatik yerleştir
        if not human1:
            self.player1.ships = setup_ai_ships()
            self.player1.update_indexes()
        if not human2:
            self.player2.ships = setup_ai_ships()
            self.player2.update_indexes()

        self.log = create_log_data(
            player1_ships=self.player1.ships,
            player2_ships=self.player2.ships
        )

        self.player1_turn = True
        self.computer_turn = not human1 or not human2
        self.over = False
        self.result = None
        self.n_shots = 0

        print("Player1 Ships:", [ship.indexes for ship in self.player1.ships])
        print("Player2 Ships:", [ship.indexes for ship in self.player2.ships])

    def make_move(self, index):
        if self.over:
            return
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1

        if player.search[index] != "U":
            return

        hit = index in opponent.indexes

        if hit:
            player.search[index] = "H"
            result = "hit"
            ship_size = None
            for ship in opponent.ships:
                result = "sunk"
                for i in ship.indexes:
                    if player.search[i] == "U":
                        result = "hit"
                        ship_size = ship.size
                        break
                if result == "sunk":
                    for i in ship.indexes:
                        player.search[i] = "S"
                    ship_size = ship.size
        else:
            player.search[index] = "M"
            result = "miss"
            ship_size = None

        self.n_shots += 1
        add_move(self.log, turn=self.n_shots, player=1 if self.player1_turn else 2,
                 index=index, result=result, ship_size=ship_size)

        if all(self.player1.search[i] != "U" for i in self.player2.indexes) or \
           all(self.player2.search[i] != "U" for i in self.player1.indexes):
            self.over = True
            self.result = 1 if self.player1_turn else 2
            finalize_log(self.log, winner=self.result)
            return

        if not hit:
            self.player1_turn = not self.player1_turn
            if self.human1 != self.human2:
                self.computer_turn = not self.computer_turn

    def random_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        if unknown:
            self.make_move(random.choice(unknown))

    def basic_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        unknown_with_neighboring_hits1 = []
        unknown_with_neighboring_hits2 = []

        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u - 10 in hits or u + 10 in hits:
                unknown_with_neighboring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u - 20 in hits or u + 20 in hits:
                unknown_with_neighboring_hits2.append(u)

        for u in unknown:
            if u in unknown_with_neighboring_hits1 and u in unknown_with_neighboring_hits2:
                self.make_move(u)
                return

        if unknown_with_neighboring_hits1:
            self.make_move(random.choice(unknown_with_neighboring_hits1))
            return

        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if checker_board:
            self.make_move(random.choice(checker_board))
            return

        self.random_ai()
