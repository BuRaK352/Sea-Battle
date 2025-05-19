import pygame
import random

# Pygame Başlatma
pygame.init()

# Ekran Boyutları
WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")

# Renkler
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Grid Boyutu ve Satır/Sütun Sayısı
GRID_SIZE = 10
SQUARE_SIZE = WIDTH // GRID_SIZE

# Font
font = pygame.font.SysFont("Arial", 30)

# Oyuncu ve Bilgisayar için Oyun Tahtaları
player_board = [['U' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # U: Unknown
computer_board = [['U' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Gemiler
ships = [5, 4, 3, 3, 2]  # Gemilerin boyutları

# Oyun Sınıfı
class Game:
    def _init_(self):
        self.player_turn = True
        self.game_over = False

    def draw_grid(self, board, x_offset=0, y_offset=0):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = WHITE
                if board[row][col] == 'H':  # Vuruş
                    color = RED
                elif board[row][col] == 'M':  # Iska
                    color = BLUE
                pygame.draw.rect(SCREEN, color, (x_offset + col * SQUARE_SIZE, y_offset + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(SCREEN, BLACK, (x_offset + col * SQUARE_SIZE, y_offset + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)

    def place_ships(self, board):
        for size in ships:
            placed = False
            while not placed:
                orientation = random.choice(["H", "V"])  # Yatay veya Dikey
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - 1)
                if orientation == "H" and col + size <= GRID_SIZE:  # Yatay yerleştirme
                    if all(board[row][col + i] == 'U' for i in range(size)):
                        for i in range(size):
                            board[row][col + i] = 'S'
                        placed = True
                elif orientation == "V" and row + size <= GRID_SIZE:  # Dikey yerleştirme
                    if all(board[row + i][col] == 'U' for i in range(size)):
                        for i in range(size):
                            board[row + i][col] = 'S'
                        placed = True

    def handle_turn(self, row, col, opponent_board):
        if opponent_board[row][col] == 'U':
            opponent_board[row][col] = 'M'  # Iska
        elif opponent_board[row][col] == 'S':
            opponent_board[row][col] = 'H'  # Vuruş

    def check_win(self, board):
        return all(cell != 'S' for row in board for cell in row)

# Oyun başlatma
game = Game()

# Gemileri yerleştir
game.place_ships(player_board)
game.place_ships(computer_board)

# Ana oyun döngüsü
running = True
while running:
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
            x, y = pygame.mouse.get_pos()
            row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
            if game.player_turn:
                # Oyuncu kendi tahtasına atış yapamaz
                if computer_board[row][col] == 'U':
                    game.handle_turn(row, col, computer_board)
                    if game.check_win(computer_board):
                        game.game_over = True
                        print("Player Wins!")
                    game.player_turn = False
            else:
                # Bilgisayarın sırası
                row, col = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                game.handle_turn(row, col, player_board)
                if game.check_win(player_board):
                    game.game_over = True
                    print("Computer Wins!")
                game.player_turn = True


                class Game:
                    def _init_(self):
                        self.player_turn = True
                        self.game_over = False  # Oyun bittiyse True olacak
                        self.winner = None  # Kazananı belirlemek için bir değişken

                    def draw_grid(self, board, x_offset=0, y_offset=0):
                        for row in range(GRID_SIZE):
                            for col in range(GRID_SIZE):
                                color = WHITE
                                if board[row][col] == 'H':  # Vuruş
                                    color = RED
                                elif board[row][col] == 'M':  # Iska
                                    color = BLUE
                                pygame.draw.rect(SCREEN, color,
                                                 (x_offset + col * SQUARE_SIZE, y_offset + row * SQUARE_SIZE,
                                                  SQUARE_SIZE, SQUARE_SIZE))
                                pygame.draw.rect(SCREEN, BLACK,
                                                 (x_offset + col * SQUARE_SIZE, y_offset + row * SQUARE_SIZE,
                                                  SQUARE_SIZE, SQUARE_SIZE), 2)

                    def place_ships(self, board):
                        for size in ships:
                            placed = False
                            while not placed:
                                orientation = random.choice(["H", "V"])  # Yatay veya Dikey
                                row = random.randint(0, GRID_SIZE - 1)
                                col = random.randint(0, GRID_SIZE - 1)
                                if orientation == "H" and col + size <= GRID_SIZE:  # Yatay yerleştirme
                                    if all(board[row][col + i] == 'U' for i in range(size)):
                                        for i in range(size):
                                            board[row][col + i] = 'S'
                                        placed = True
                                elif orientation == "V" and row + size <= GRID_SIZE:  # Dikey yerleştirme
                                    if all(board[row + i][col] == 'U' for i in range(size)):
                                        for i in range(size):
                                            board[row + i][col] = 'S'
                                        placed = True

                    def handle_turn(self, row, col, opponent_board):
                        if opponent_board[row][col] == 'U':
                            opponent_board[row][col] = 'M'  # Iska
                        elif opponent_board[row][col] == 'S':
                            opponent_board[row][col] = 'H'  # Vuruş

                    def check_win(self, board):
                        """Tüm gemiler batmış mı kontrol et"""
                        return all(cell != 'S' for row in board for cell in row)

                    def update_game_status(self):
                        """Oyun bitip bitmediğini kontrol et"""
                        if self.check_win(player_board):
                            self.game_over = True
                            self.winner = "Player"
                        elif self.check_win(computer_board):
                            self.game_over = True
                            self.winner = "Computer"

    # Ekrana çizim
    game.draw_grid(player_board, 50, 50)  # Oyuncu tahtası
    game.draw_grid(computer_board, 50 + GRID_SIZE * SQUARE_SIZE + 50, 50)  # Bilgisayar tahtası

    pygame.display.flip()

pygame.quit()
