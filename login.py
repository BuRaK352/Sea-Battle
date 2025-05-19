# login.py
import pygame
import sys
from log_helper import set_username, load_user_info

pygame.init()
pygame.font.init()

Display_resolution = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = Display_resolution.current_w, Display_resolution.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Battleship - Giriş")

FONT = pygame.font.SysFont("arial", 36)
INPUT_FONT = pygame.font.SysFont("arial", 28)

WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (50, 150, 255)
GREEN = (0, 200, 100)

def draw_text(surface, text, pos, font, color=WHITE):
    label = font.render(text, True, color)
    surface.blit(label, pos)

def login_screen():
    # Otomatik giriş denemesi
    user_info = load_user_info()
    if user_info:
        last_username = list(user_info.keys())[0]  # İlk kullanıcıyı al
        set_username(last_username)
        return last_username

    # Giriş ekranı
    input_width, input_height = 400, 50
    button_width, button_height = 200, 50

    input_box = pygame.Rect(
        (SCREEN_WIDTH - input_width) // 2,
        (SCREEN_HEIGHT - input_height) // 2,
        input_width,
        input_height
    )

    button_rect = pygame.Rect(
        (SCREEN_WIDTH - button_width) // 2,
        input_box.y + input_height + 40,
        button_width,
        button_height
    )

    prompt_text = "Lütfen adınızı girin:"
    prompt_surface = FONT.render(prompt_text, True, WHITE)
    prompt_pos = (
        (SCREEN_WIDTH - prompt_surface.get_width()) // 2,
        input_box.y - 80
    )

    color_active = BLUE
    color_passive = GRAY
    color = color_passive
    active = False
    user_text = ""

    clock = pygame.time.Clock()
    while True:
        SCREEN.fill((30, 30, 30))
        SCREEN.blit(prompt_surface, prompt_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_passive

                if button_rect.collidepoint(event.pos) and user_text.strip():
                    set_username(user_text.strip())
                    return user_text.strip()

            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif len(user_text) < 20:
                    user_text += event.unicode

        pygame.draw.rect(SCREEN, color, input_box, 2)
        draw_text(SCREEN, user_text, (input_box.x + 10, input_box.y + 10), INPUT_FONT)

        pygame.draw.rect(SCREEN, GREEN, button_rect, border_radius=8)
        draw_text(SCREEN, "Devam Et", (button_rect.x + 40, button_rect.y + 10), INPUT_FONT)

        pygame.display.flip()
        clock.tick(30)
