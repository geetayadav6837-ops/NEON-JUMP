
import pygame
import random
import os
import math
from array import array

pygame.init()

# ---------------- BASIC SETTINGS ----------------

WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON JUMP")

clock = pygame.time.Clock()

BLACK = (5, 8, 25)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
PINK = (255, 0, 180)
GREEN = (0, 255, 100)
YELLOW = (255, 230, 0)
PURPLE = (150, 0, 255)

font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 42, bold=True)
small_font = pygame.font.SysFont("Arial", 17, bold=True)

# ---------------- SOUND + BACKGROUND MUSIC ----------------

sound_on = True
music_on = True

coin_sound = None
music_sound = None
music_channel = None

try:
    pygame.mixer.init(
        frequency=22050,
        size=-16,
        channels=1
    )

    # Coin sound
    coin_data = array('h')

    for i in range(3000):
        value = int(
            10000 * math.sin(
                2 * math.pi * 700 * i / 22050
            )
        )
        coin_data.append(value)

    coin_sound = pygame.mixer.Sound(buffer=coin_data)

    # Electronic Neon Music
    sample_rate = 22050
    duration = 4
    music_data = array('h')

    melody = [440, 523, 659, 784, 659, 523, 587, 784]
    bass = [110, 110, 147, 147, 165, 165, 147, 147]

    for i in range(sample_rate * duration):

        t = i / sample_rate
        beat = int(t * 2) % 8

        bass_wave = math.sin(
            2 * math.pi * bass[beat] * t
        )

        melody_wave = math.sin(
            2 * math.pi * melody[beat] * t
        )

        kick_phase = (t * 2) % 1

        kick = math.sin(
            2 * math.pi * 70 * kick_phase
        ) * math.exp(-kick_phase * 9)

        value = int(
            3500 * bass_wave +
            1800 * melody_wave +
            2200 * kick
        )

        value = max(-12000, min(12000, value))
        music_data.append(value)

    music_sound = pygame.mixer.Sound(buffer=music_data)
    music_sound.set_volume(0.25)

    music_channel = pygame.mixer.Channel(1)

except Exception as e:
    print("Audio Error:", e)


# ---------------- HIGH SCORE ----------------

high_score = 0

if os.path.exists("highscore.txt"):
    try:
        with open("highscore.txt", "r") as file:
            high_score = int(file.read())
    except:
        high_score = 0


def save_high_score():
    global high_score

    if score > high_score:
        high_score = score

        try:
            with open("highscore.txt", "w") as file:
                file.write(str(high_score))
        except:
            pass


# ---------------- BACKGROUND ----------------

stars = []

for i in range(55):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])


def draw_background():
    screen.fill(BLACK)

    for star in stars:
        pygame.draw.circle(
            screen,
            (80, 100, 150),
            (star[0], star[1]),
            star[2]
        )

        star[1] += 0.3

        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)


# ---------------- MUSIC CONTROL ----------------

def update_music():

    if music_channel is None or music_sound is None:
        return

    should_play = (
        music_on and
        game_state in ("menu", "settings", "game")
    )

    if should_play:
        if not music_channel.get_busy():
            music_channel.play(music_sound, loops=-1)
    else:
        if music_channel.get_busy():
            music_channel.stop()


# ---------------- TEXT ----------------

def draw_text(text, font_type, color, x, y):
    image = font_type.render(text, True, color)
    rect = image.get_rect(center=(x, y))
    screen.blit(image, rect)


# ---------------- BUTTON ----------------

def draw_button(text, x, y, w, h, color):
    rect = pygame.Rect(x, y, w, h)

    pygame.draw.rect(
        screen, color, rect,
        border_radius=15
    )

    pygame.draw.rect(
        screen, WHITE, rect,
        2, border_radius=15
    )

    draw_text(
        text, font, WHITE,
        x + w // 2, y + h // 2
    )

    return rect


# ---------------- PARTICLES ----------------

particles = []


def create_particles(x, y, color):
    for i in range(12):
        particles.append([
            x, y,
            random.uniform(-3, 3),
            random.uniform(-4, 2),
            30, color
        ])


def update_particles():
    for p in particles[:]:

        p[0] += p[2]
        p[1] += p[3]
        p[3] += 0.15
        p[4] -= 1

        if p[4] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(
                screen,
                p[5],
                (int(p[0]), int(p[1])),
                3
            )


# ---------------- GAME VARIABLES ----------------

player = pygame.Rect(180, 450, 35, 40)

velocity = 0
gravity = 0.35
jump_power = -10

platforms = []
coins = []

score = 0
camera = 0

rocket_timer = 0
shield_active = False
next_reward_score = 100

game_state = "menu"


# ---------------- RESET GAME ----------------

def reset_game():
    global player, velocity, platforms, coins
    global score, camera, rocket_timer
    global shield_active, next_reward_score
    global particles

    player = pygame.Rect(180, 450, 35, 40)

    velocity = 0
    score = 0
    camera = 0

    rocket_timer = 0
    shield_active = False
    next_reward_score = 100

    particles = []
    platforms = []
    coins = []

    platforms.append(
        pygame.Rect(140, 520, 110, 15)
    )

    for i in range(9):
        x = random.randint(10, 290)
        y = 450 - i * 65

        platforms.append(
            pygame.Rect(x, y, 90, 15)
        )

    for i in range(6):
        x = random.randint(20, 350)
        y = 400 - i * 100

        coins.append(
            pygame.Rect(x, y, 18, 18)
        )


# ---------------- DRAW PLAYER ----------------

def draw_player():

    pygame.draw.circle(
        screen, CYAN,
        (player.centerx, player.centery), 23
    )

    pygame.draw.circle(
        screen, WHITE,
        (player.centerx - 7, player.centery - 5), 5
    )

    pygame.draw.circle(
        screen, WHITE,
        (player.centerx + 7, player.centery - 5), 5
    )

    pygame.draw.circle(
        screen, BLACK,
        (player.centerx - 7, player.centery - 5), 2
    )

    pygame.draw.circle(
        screen, BLACK,
        (player.centerx + 7, player.centery - 5), 2
    )

    pygame.draw.arc(
        screen, BLACK,
        (player.centerx - 9, player.centery, 18, 12),
        3.3, 6.1, 2
    )


# ---------------- DRAW GAME ----------------

def draw_game():

    draw_background()

    for p in platforms:

        pygame.draw.rect(
            screen, CYAN, p,
            border_radius=7
        )

        pygame.draw.rect(
            screen, WHITE, p,
            2, border_radius=7
        )

    for coin in coins:

        pygame.draw.circle(
            screen, YELLOW,
            coin.center, 11
        )

        pygame.draw.circle(
            screen, WHITE,
            coin.center, 5
        )

    draw_player()
    update_particles()

    draw_text(
        "SCORE: " + str(score),
        font, WHITE, 80, 30
    )

    draw_text(
        "BEST: " + str(high_score),
        small_font, YELLOW, 305, 30
    )

    draw_text(
        "NEXT: " + str(next_reward_score),
        small_font, CYAN, 200, 65
    )

    if rocket_timer > 0:
        draw_text(
            "ROCKET BOOST!",
            small_font, PINK, 200, 95
        )

    if shield_active:
        draw_text(
            "SHIELD ACTIVE!",
            small_font, GREEN, 200, 120
        )

    # Pause button
    pygame.draw.rect(
        screen, PURPLE,
        (345, 75, 42, 42),
        border_radius=10
    )

    draw_text("II", font, WHITE, 366, 96)

    # Mobile controls
    pygame.draw.circle(
        screen, PURPLE, (65, 535), 35
    )

    pygame.draw.circle(
        screen, PURPLE, (335, 535), 35
    )

    draw_text("<", big_font, WHITE, 65, 535)
    draw_text(">", big_font, WHITE, 335, 535)


# ---------------- UPDATE GAME ----------------

def update_game(left, right):
    global velocity, camera, score
    global rocket_timer, shield_active
    global next_reward_score, game_state

    if left:
        player.x -= 5

    if right:
        player.x += 5

    if player.right < 0:
        player.left = WIDTH

    if player.left > WIDTH:
        player.right = 0

    old_bottom = player.bottom

    velocity += gravity

    if rocket_timer > 0:
        velocity = -15
        rocket_timer -= 1

    player.y += int(velocity)

    # Platform collision
    if velocity > 0:

        for p in platforms:

            if (
                player.right > p.left and
                player.left < p.right and
                old_bottom <= p.top and
                player.bottom >= p.top
            ):

                player.bottom = p.top
                velocity = jump_power

    # Camera
    if player.y < 250:

        difference = 250 - player.y
        player.y = 250

        camera += difference

        for p in platforms:
            p.y += difference

        for coin in coins:
            coin.y += difference

        score = max(score, camera // 10)

    # Remove old platforms
    for p in platforms[:]:

        if p.top > HEIGHT:
            platforms.remove(p)

    # Create platforms
    while len(platforms) < 9:

        x = random.randint(10, 290)
        y = min(p.y for p in platforms) - random.randint(55, 75)

        platforms.append(
            pygame.Rect(x, y, 90, 15)
        )

    # Remove old coins
    for coin in coins[:]:

        if coin.top > HEIGHT:
            coins.remove(coin)

    # Create coins
    while len(coins) < 6:

        x = random.randint(20, 350)
        y = random.randint(-100, -30)

        coins.append(
            pygame.Rect(x, y, 18, 18)
        )

    # Collect coins
    for coin in coins[:]:

        if player.colliderect(coin):

            coins.remove(coin)
            score += 10

            create_particles(
                coin.centerx,
                coin.centery,
                YELLOW
            )

            if sound_on and coin_sound:
                coin_sound.play()

    # Every 100 score reward
    if score >= next_reward_score:

        rocket_timer = 180
        shield_active = True

        create_particles(
            player.centerx,
            player.centery,
            PINK
        )

        next_reward_score += 100

    # Shield protection
    if player.top > HEIGHT:

        if shield_active:

            shield_active = False
            player.y = 300
            velocity = jump_power

            create_particles(
                player.centerx,
                player.centery,
                GREEN
            )

        else:

            save_high_score()
            game_state = "gameover"

    save_high_score()


# ---------------- MAIN MENU ----------------

def draw_menu():

    draw_background()

    draw_text("NEON", big_font, CYAN, 200, 125)
    draw_text("JUMP", big_font, PINK, 200, 175)

    draw_text(
        "THE ULTIMATE JUMP GAME",
        small_font, WHITE, 200, 220
    )

    play_button = draw_button(
        "PLAY", 110, 290, 180, 55, CYAN
    )

    settings_button = draw_button(
        "SETTINGS", 110, 365, 180, 55, PURPLE
    )

    draw_text(
        "BEST SCORE: " + str(high_score),
        small_font, YELLOW, 200, 455
    )

    draw_text(
        "Made with Python + Pygame",
        small_font, WHITE, 200, 550
    )

    return play_button, settings_button


# ---------------- SETTINGS ----------------

def draw_settings():

    draw_background()

    draw_text(
        "SETTINGS", big_font, CYAN, 200, 150
    )

    music_text = "MUSIC: ON" if music_on else "MUSIC: OFF"

    music_button = draw_button(
        music_text, 85, 270, 230, 55, PURPLE
    )

    back_button = draw_button(
        "BACK", 110, 365, 180, 55, PINK
    )

    draw_text(
        "Electronic Neon Music",
        small_font, WHITE, 200, 480
    )

    return music_button, back_button


# ---------------- PAUSE MENU ----------------

def draw_pause():

    draw_background()

    draw_text(
        "GAME PAUSED",
        big_font, CYAN, 200, 175
    )

    resume_button = draw_button(
        "RESUME", 100, 260, 200, 55, GREEN
    )

    menu_button = draw_button(
        "MAIN MENU", 100, 345, 200, 55, PURPLE
    )

    draw_text(
        "Your game is safe!",
        small_font, WHITE, 200, 440
    )

    return resume_button, menu_button


# ---------------- GAME OVER ----------------

def draw_gameover():

    draw_background()

    draw_text(
        "GAME OVER",
        big_font, PINK, 200, 190
    )

    draw_text(
        "SCORE: " + str(score),
        font, WHITE, 200, 260
    )

    draw_text(
        "BEST: " + str(high_score),
        font, YELLOW, 200, 305
    )

    restart_button = draw_button(
        "PLAY AGAIN", 90, 380, 220, 55, CYAN
    )

    menu_button = draw_button(
        "MAIN MENU", 90, 455, 220, 55, PURPLE
    )

    return restart_button, menu_button


# ---------------- START GAME ----------------

reset_game()

running = True

while running:

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    left = False
    right = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            save_high_score()
            running = False

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            pos = event.pos

            if game_state == "game":

                pause_rect = pygame.Rect(
                    345, 75, 42, 42
                )

                if pause_rect.collidepoint(pos):
                    game_state = "pause"

            elif game_state == "pause":

                if pygame.Rect(
                    100, 260, 200, 55
                ).collidepoint(pos):

                    game_state = "game"

                elif pygame.Rect(
                    100, 345, 200, 55
                ).collidepoint(pos):

                    game_state = "menu"

            elif game_state == "menu":

                if pygame.Rect(
                    110, 290, 180, 55
                ).collidepoint(pos):

                    reset_game()
                    game_state = "game"

                elif pygame.Rect(
                    110, 365, 180, 55
                ).collidepoint(pos):

                    game_state = "settings"

            elif game_state == "settings":

                if pygame.Rect(
                    85, 270, 230, 55
                ).collidepoint(pos):

                    music_on = not music_on

                elif pygame.Rect(
                    110, 365, 180, 55
                ).collidepoint(pos):

                    game_state = "menu"

            elif game_state == "gameover":

                if pygame.Rect(
                    90, 380, 220, 55
                ).collidepoint(pos):

                    reset_game()
                    game_state = "game"

                elif pygame.Rect(
                    90, 455, 220, 55
                ).collidepoint(pos):

                    game_state = "menu"

        # Keyboard controls
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == "game":
                    game_state = "pause"

                elif game_state == "pause":
                    game_state = "game"

    # GAME SCREEN
    if game_state == "game":

        keys = pygame.key.get_pressed()

        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]

        # Mobile touch controls
        if mouse_pressed:

            if mouse_pos[0] < 130 and mouse_pos[1] > 450:
                left = True

            elif mouse_pos[0] > 270 and mouse_pos[1] > 450:
                right = True

        update_game(left, right)
        draw_game()

    elif game_state == "menu":

        draw_menu()

    elif game_state == "settings":

        draw_settings()

    elif game_state == "pause":

        draw_pause()

    elif game_state == "gameover":

        draw_gameover()

    # Background music control
    update_music()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
