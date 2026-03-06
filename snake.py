import pygame
import time
import random
import os
import math
import sys
import scoreboard

# Initialiseer Pygame
pygame.init()
scoreboard.init_db()

def get_resource_path(relative_path):
    """ Haal absoluut pad naar bron op """
    try:
        # PyInstaller maakt een tijdelijke map aan en slaat het pad op in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
GRAY = (200, 200, 200)
DARK_BG = (25, 25, 30)
GRID_COLOR = (40, 40, 50)

# Scherm afmetingen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Best Education B.V.")

clock = pygame.time.Clock()

SNAKE_BLOCK = 20
INITIAL_SPEED = 10
MAX_SCORE_TO_WIN = 50

# Lettertypen
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
title_font = pygame.font.SysFont("bahnschrift", 50)

def create_hex_bg(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(DARK_BG)
    hex_size = 25
    x_offset = math.sqrt(3) * hex_size
    y_offset = 1.5 * hex_size
    for row in range(int(h / y_offset) + 2):
        for col in range(int(w / x_offset) + 2):
            cx = col * x_offset
            if row % 2 == 1:
                cx += x_offset / 2
            cy = row * y_offset
            points = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                points.append((cx + hex_size * math.cos(angle), cy + hex_size * math.sin(angle)))
            pygame.draw.polygon(surf, GRID_COLOR, points, 2)
    return surf

bg_surface = create_hex_bg(WIDTH, HEIGHT)

def draw_apple(surface, x, y, size):
    center = (int(x + size/2), int(y + size/2))
    radius = int(size/2)
    pygame.draw.circle(surface, RED, center, radius)
    pygame.draw.circle(surface, (255, 100, 100), (center[0]-3, center[1]-3), int(radius/3))
    pygame.draw.ellipse(surface, (40, 200, 40), [center[0], center[1]-radius-2, 8, 5])

def draw_obstacle(surface, x, y, size):
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, (100, 100, 100), rect, border_radius=4)
    pygame.draw.rect(surface, (150, 150, 150), rect, 2, border_radius=4)
    # Geef het een rotsachtige uitstraling met enkele binnenste lijnen
    pygame.draw.line(surface, (70, 70, 70), (x+5, y+5), (x+size-5, y+size-5), 2)
    pygame.draw.line(surface, (70, 70, 70), (x+size-5, y+5), (x+5, y+size-5), 2)

def message(msg, color, y_displace=0, font=font_style):
    mesg = font.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_displace))
    screen.blit(mesg, mesg_rect)

def draw_snake(snake_block, snake_list, dx, dy):
    for i, x in enumerate(snake_list):
        color = GREEN if i != len(snake_list)-1 else (0, 200, 0)
        pygame.draw.rect(screen, color, [x[0], x[1], snake_block, snake_block], border_radius=4)
        if i == len(snake_list) - 1:
            head_x, head_y = x[0], x[1]
            if dx > 0:
                e1, e2 = (head_x + snake_block - 5, head_y + 5), (head_x + snake_block - 5, head_y + snake_block - 5)
            elif dx < 0:
                e1, e2 = (head_x + 5, head_y + 5), (head_x + 5, head_y + snake_block - 5)
            elif dy > 0:
                e1, e2 = (head_x + 5, head_y + snake_block - 5), (head_x + snake_block - 5, head_y + snake_block - 5)
            else:
                e1, e2 = (head_x + 5, head_y + 5), (head_x + snake_block - 5, head_y + 5)
                
            pygame.draw.circle(screen, WHITE, e1, 4)
            pygame.draw.circle(screen, WHITE, e2, 4)
            pygame.draw.circle(screen, BLACK, e1, 2)
            pygame.draw.circle(screen, BLACK, e2, 2)

def game_intro():
    intro = True
    
    # Probeer het logo te laden
    logo_path = get_resource_path(os.path.join("Bijlage 2 - Logos", "Bijlage 2 - Logo.png"))
    logo = None
    if os.path.exists(logo_path):
        try:
            logo = pygame.image.load(logo_path)
            logo = pygame.transform.scale(logo, (300, int(300 * logo.get_height() / logo.get_width())))
        except Exception as e:
            print("Could not load logo:", e)

    while intro:
        screen.blit(bg_surface, (0, 0))
        if logo:
            logo_rect = logo.get_rect(center=(WIDTH/2, HEIGHT/4))
            screen.blit(logo, logo_rect)
        
        message("Best Education B.V.", WHITE, -50, title_font)
        message("Wij lanceren je de toekomst in!", WHITE, 10)
        message("Press SPACE to Start or ESC to Quit", RED, 80)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    intro = False

def input_email_screen(score, won):
    email = ""
    input_active = True
    
    while input_active:
        screen.blit(bg_surface, (0, 0))
        if won:
            message("VICTORY!", GREEN, -150, title_font)
        else:
            message("GAME OVER", RED, -150, title_font)
            
        message(f"Your Score: {score}", WHITE, -80)
        message("Enter your email for the scoreboard:", BLUE, -20)
        
        # Teken invoerveld
        input_rect = pygame.Rect(WIDTH/2 - 200, HEIGHT/2 + 20, 400, 40)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        
        email_surf = font_style.render(email, True, BLACK)
        screen.blit(email_surf, (input_rect.x + 5, input_rect.y + 5))
        
        message("Press ENTER to submit, or ESC to skip", WHITE, 100)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    return email
                elif event.key == pygame.K_BACKSPACE:
                    email = email[:-1]
                else:
                    if len(email) < 50:
                        email += event.unicode


def view_scoreboard():
    viewing = True
    scores = scoreboard.get_top_scores()
    
    while viewing:
        screen.blit(bg_surface, (0, 0))
        message("TOP 10 SCOREBOARD", BLUE, -250, title_font)
        
        y_offset = -180
        for i, (email, score, date) in enumerate(scores):
            # Maskeer e-mail optioneel voor privacy, of toon slechts een deel ervan
            display_email = email if len(email) <= 20 else email[:17] + "..."
            entry_text = f"{i+1}. {display_email} - Score: {score}"
            message(entry_text, WHITE, y_offset, font_style)
            y_offset += 35
            
        message("Press SPACE to Play Again or ESC to Quit", RED, 220)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    viewing = False


def gameLoop():
    game_over = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    
    score = 0
    current_speed = INITIAL_SPEED
    obstacles = []

    foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 20.0) * 20.0
    foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 20.0) * 20.0
    
    # Voorkom dat voedsel op exact de startpositie spawnt
    while foodx == x1 and foody == y1:
        foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 20.0) * 20.0
        foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 20.0) * 20.0

    while not game_over:
        while game_close == True:
            # Verwerk e-mailinvoer na einde spel
            won = score >= MAX_SCORE_TO_WIN
            entered_email = input_email_screen(score, won)
            
            if entered_email:
                scoreboard.add_score(entered_email, score)
                
            view_scoreboard()
            return # Herstart spel vanaf __main__

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and x1_change == 0:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and x1_change == 0:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and y1_change == 0:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and y1_change == 0:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0

        # Grenscontroles
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
            
        x1 += x1_change
        y1 += y1_change
        screen.blit(bg_surface, (0, 0))
        draw_apple(screen, foodx, foody, SNAKE_BLOCK)
        
        for obs in obstacles:
            draw_obstacle(screen, obs[0], obs[1], SNAKE_BLOCK)

        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Controle op botsing met zichzelf
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True
                
        # Controle op botsing met obstakel
        for obs in obstacles:
            if snake_Head[0] == obs[0] and snake_Head[1] == obs[1]:
                game_close = True

        draw_snake(SNAKE_BLOCK, snake_List, x1_change, y1_change)
        
        # Toon Score
        score_surf = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, [10, 10])

        pygame.display.update()

        # Controle of voedsel is gegeten
        if x1 == foodx and y1 == foody:
            Length_of_snake += 1
            score += 1
            current_speed += 0.5 # Progressieve moeilijkheidsgraad
            
            # Spawn obstakel per 5 punten
            if score > 0 and score % 5 == 0:
                obs_length = random.randint(3, 8) if score < 30 else random.randint(5, 10)
                
                valid_obs_start = False
                while not valid_obs_start:
                    obs_x = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 20.0) * 20.0
                    obs_y = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 20.0) * 20.0
                    
                    if [obs_x, obs_y] not in snake_List and (obs_x, obs_y) != (foodx, foody) and (obs_x, obs_y) not in obstacles:
                        valid_obs_start = True
                
                # Laat het obstakel dynamisch groeien
                current_obs_chain = [(obs_x, obs_y)]
                
                for _ in range(obs_length - 1):
                    last_x, last_y = current_obs_chain[-1]
                    # Richtingen: OMHOOG, OMLAAG, LINKS, RECHTS
                    directions = [(0, -SNAKE_BLOCK), (0, SNAKE_BLOCK), (-SNAKE_BLOCK, 0), (SNAKE_BLOCK, 0)]
                    random.shuffle(directions)
                    
                    added = False
                    for dx, dy in directions:
                        nx, ny = last_x + dx, last_y + dy
                        # Controleer grenzen
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                            # Controleer overlap
                            if [nx, ny] not in snake_List and (nx, ny) != (foodx, foody) and (nx, ny) not in obstacles and (nx, ny) not in current_obs_chain:
                                current_obs_chain.append((nx, ny))
                                added = True
                                break
                    if not added:
                        break # Kon obstakel niet verder in enige richting laten groeien
                
                obstacles.extend(current_obs_chain)

            # Respawn voedsel
            valid_food = False
            while not valid_food:
                foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 20.0) * 20.0
                foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 20.0) * 20.0
                if [foodx, foody] not in snake_List and (foodx, foody) not in obstacles:
                    valid_food = True

            if score >= MAX_SCORE_TO_WIN:
                game_close = True

        clock.tick(current_speed)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_intro()
    while True:
        gameLoop()
