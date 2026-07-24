# <===== Import the Useful Libraries for Snake Game =====>

import pygame
import random
import sys
import math

# ─────────────────────────────────────────────
#  Initialize
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
SNAKE_SIZE     = 20
GRID_W         = WIDTH  // SNAKE_SIZE   # 64
GRID_H         = HEIGHT // SNAKE_SIZE   # 36

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Pro  |  10 Levels")
clock = pygame.time.Clock()

# ─────────────────────────────────────────────
#  Fonts
# ─────────────────────────────────────────────
font_huge  = pygame.font.SysFont("consolas", 72, bold=True)
font_large = pygame.font.SysFont("consolas", 42, bold=True)
font_med   = pygame.font.SysFont("consolas", 28)
font_small = pygame.font.SysFont("consolas", 20)

# ─────────────────────────────────────────────
#  Colour palette
# ─────────────────────────────────────────────
C_BG        = (10,  12,  20)
C_GRID      = (20,  24,  38)
C_SNAKE_H   = (0,   255, 140)
C_SNAKE_B   = (0,   200, 100)
C_FOOD      = (255,  60,  60)
C_FOOD2     = (255, 180,   0)
C_OBSTACLE  = (80,  80, 100)
C_OBS_EDGE  = (140, 140, 180)
C_WHITE     = (255, 255, 255)
C_GOLD      = (255, 215,   0)
C_CYAN      = (0,   220, 255)
C_DARK      = (6,    8,  14)

# ─────────────────────────────────────────────
#  Level definitions:  (speed, num_obstacles, walls_deadly)
# ─────────────────────────────────────────────
LEVEL_CONFIG = [
    (8,   0,  False),   # 1 – open, slow, wrap walls
    (10,  3,  False),   # 2
    (11,  5,  False),   # 3
    (12,  6,  True),    # 4 – walls now kill
    (13,  8,  True),    # 5
    (14, 10,  True),    # 6
    (15, 12,  True),    # 7
    (16, 14,  True),    # 8
    (17, 16,  True),    # 9
    (18, 20,  True),    # 10 – max chaos
]

SCORE_PER_FOOD   = 10
BONUS_SCORE      = 25
BONUS_CHANCE     = 0.15
LEVEL_UP_SCORE   = 50   # points needed IN THIS LEVEL to advance

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def rand_cell():
    return (random.randint(1, GRID_W - 2) * SNAKE_SIZE,
            random.randint(1, GRID_H - 2) * SNAKE_SIZE)

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_rounded_rect(surface, color, rect, radius=6):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

# ─────────────────────────────────────────────
#  Obstacle generation
# ─────────────────────────────────────────────
SAFE_ZONE = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 - 120, 240, 240)

def generate_obstacles(count):
    obs = []
    attempts = 0
    while len(obs) < count and attempts < 2000:
        attempts += 1
        gx = random.randint(1, GRID_W - 4)
        gy = random.randint(2, GRID_H - 3)   # avoid top HUD row
        w  = random.randint(1, 3)
        h  = random.randint(1, 3)
        rect = pygame.Rect(gx * SNAKE_SIZE, gy * SNAKE_SIZE,
                           w * SNAKE_SIZE, h * SNAKE_SIZE)
        if SAFE_ZONE.colliderect(rect):
            continue
        obs.append(rect)
    return obs

# ─────────────────────────────────────────────
#  Particles
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x + SNAKE_SIZE // 2
        self.y = y + SNAKE_SIZE // 2
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life  = 1.0
        self.decay = random.uniform(0.04, 0.09)
        self.size  = random.randint(3, 7)
        self.color = color

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        c = lerp_color(self.color, C_BG, 1 - self.life)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)

particles = []

def spawn_particles(x, y, color, n=18):
    for _ in range(n):
        particles.append(Particle(x, y, color))

# ─────────────────────────────────────────────
#  Draw helpers
# ─────────────────────────────────────────────
def draw_bg():
    screen.fill(C_BG)
    for gx in range(GRID_W + 1):
        pygame.draw.line(screen, C_GRID, (gx * SNAKE_SIZE, 0), (gx * SNAKE_SIZE, HEIGHT))
    for gy in range(GRID_H + 1):
        pygame.draw.line(screen, C_GRID, (0, gy * SNAKE_SIZE), (WIDTH, gy * SNAKE_SIZE))

def draw_snake(snake_list):
    n = len(snake_list)
    for i, block in enumerate(snake_list):
        t = i / max(n - 1, 1)
        color = lerp_color(C_SNAKE_B, C_SNAKE_H, t)
        r = pygame.Rect(block[0] + 1, block[1] + 1, SNAKE_SIZE - 2, SNAKE_SIZE - 2)
        draw_rounded_rect(screen, color, r, radius=5)
    if snake_list:
        hx, hy = snake_list[-1]
        pygame.draw.circle(screen, C_WHITE, (hx + 5,  hy + 6), 4)
        pygame.draw.circle(screen, C_WHITE, (hx + 14, hy + 6), 4)
        pygame.draw.circle(screen, C_DARK,  (hx + 5,  hy + 6), 2)
        pygame.draw.circle(screen, C_DARK,  (hx + 14, hy + 6), 2)

def draw_food(fx, fy, tick, bonus=False):
    color  = C_FOOD2 if bonus else C_FOOD
    pulse  = abs(math.sin(tick * 0.08)) * 3
    cx, cy = fx + SNAKE_SIZE // 2, fy + SNAKE_SIZE // 2
    r = int(SNAKE_SIZE // 2 + pulse)
    pygame.draw.circle(screen, color, (cx, cy), r)
    pygame.draw.circle(screen, C_WHITE, (cx - 3, cy - 3), 3)

def draw_obstacles(obs_list):
    for rect in obs_list:
        draw_rounded_rect(screen, C_OBSTACLE, rect, radius=4)
        pygame.draw.rect(screen, C_OBS_EDGE, rect, 2, border_radius=4)

def draw_hud(score, level, high_score, closed_walls):
    panel = pygame.Surface((WIDTH, 48), pygame.SRCALPHA)
    panel.fill((18, 22, 36, 220))
    screen.blit(panel, (0, 0))
    screen.blit(font_med.render(f"Score: {score}", True, C_GOLD),  (20, 10))
    lv_surf = font_med.render(f"Level {level}/10", True, C_CYAN)
    screen.blit(lv_surf, (WIDTH // 2 - lv_surf.get_width() // 2, 10))
    hs_surf = font_med.render(f"Best: {high_score}", True, C_WHITE)
    screen.blit(hs_surf, (WIDTH - hs_surf.get_width() - 20, 10))
    if closed_walls:
        wi = font_small.render("WALLS DEADLY  |  P=Pause", True, C_FOOD)
        screen.blit(wi, (WIDTH // 2 - wi.get_width() // 2, 32))
    else:
        wi = font_small.render("Walls: Wrap-Around  |  P=Pause", True, (120,200,120))
        screen.blit(wi, (WIDTH // 2 - wi.get_width() // 2, 32))

def centered(text, font, color, y, shadow=True):
    if shadow:
        sh = font.render(text, True, C_DARK)
        screen.blit(sh, (WIDTH//2 - sh.get_width()//2 + 3, y + 3))
    s = font.render(text, True, color)
    screen.blit(s, (WIDTH//2 - s.get_width()//2, y))

# ─────────────────────────────────────────────
#  TITLE SCREEN
# ─────────────────────────────────────────────
def title_screen():
    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        screen.fill(C_BG)
        for i in range(0, WIDTH, SNAKE_SIZE):
            for j in range(0, HEIGHT, SNAKE_SIZE):
                b = int(5 + 5 * math.sin((i + j + tick) * 0.05))
                pygame.draw.rect(screen, (b, b + 5, b + 15),
                                 (i, j, SNAKE_SIZE - 1, SNAKE_SIZE - 1))

        centered("SNAKE  PRO", font_huge,
                 lerp_color(C_SNAKE_H, C_CYAN, abs(math.sin(tick * 0.03))), 160)
        centered("10 LEVELS  |  OBSTACLES  |  BONUS FOOD", font_med, C_WHITE, 280)
        centered("WASD / Arrow Keys = Move     P = Pause     ESC = Quit",
                 font_small, (160,160,200), 340)
        if (tick // 30) % 2 == 0:
            centered(">>>  PRESS  ENTER  TO  START  <<<", font_large, C_GOLD, 430)

        # level strip
        for lv in range(10):
            cx = 90 + lv * 110
            cy = 590
            c = lerp_color(C_SNAKE_H, C_FOOD, lv / 9)
            pygame.draw.rect(screen, c, (cx, cy, 90, 40), border_radius=8)
            t = font_small.render(f"Lv {lv+1}", True, C_DARK)
            screen.blit(t, (cx + 45 - t.get_width()//2, cy + 10))

        pygame.display.flip()
        clock.tick(60)
        tick += 1

# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────
def game_over_screen(score, high_score, level, win=False):
    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN): return "retry"
                if event.key == pygame.K_m:                     return "menu"
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        screen.fill(C_DARK)
        title  = "YOU  WIN!" if win else "GAME  OVER"
        tcolor = C_GOLD      if win else C_FOOD
        centered(title,                     font_huge,  tcolor,  160)
        centered(f"Score :  {score}",       font_large, C_WHITE, 280)
        centered(f"Level Reached :  {level}", font_med, C_CYAN,  350)
        centered(f"Best  :  {high_score}",  font_med,   C_GOLD,  400)
        if (tick // 30) % 2 == 0:
            centered("R / ENTER = Retry     M = Menu     ESC = Quit",
                     font_med, (180,180,220), 500)
        pygame.display.flip()
        clock.tick(60)
        tick += 1

# ─────────────────────────────────────────────
#  PAUSE
# ─────────────────────────────────────────────
def pause_screen():
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    screen.blit(ov, (0, 0))
    centered("PAUSED", font_huge, C_CYAN, 260)
    centered("Press P to Resume", font_med, C_WHITE, 380)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p: return

# ─────────────────────────────────────────────
#  LEVEL TRANSITION
# ─────────────────────────────────────────────
def level_transition(level):
    for a in range(0, 256, 10):
        ov = pygame.Surface((WIDTH, HEIGHT))
        ov.set_alpha(a)
        ov.fill(C_DARK)
        screen.blit(ov, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1600:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        screen.fill(C_DARK)
        centered(f"LEVEL  {level}", font_huge, C_GOLD, 220)
        bar = "Speed:  " + chr(9608) * level + chr(9617) * (10 - level)
        centered(bar, font_med, C_CYAN, 350)
        obs = LEVEL_CONFIG[level - 1][1]
        wall_txt = "Walls: DEADLY" if LEVEL_CONFIG[level-1][2] else "Walls: Wrap-Around"
        centered(f"Obstacles: {obs}     {wall_txt}", font_med, C_FOOD, 400)
        centered(f"Eat {LEVEL_UP_SCORE} pts to advance", font_small, (160,160,200), 460)
        pygame.display.flip()
        clock.tick(60)

# ─────────────────────────────────────────────
#  Collision helpers
# ─────────────────────────────────────────────
def on_obstacle(x, y, obstacles):
    r = pygame.Rect(x, y, SNAKE_SIZE, SNAKE_SIZE)
    return any(r.colliderect(o) for o in obstacles)

def safe_food(snake_list, obstacles):
    for _ in range(600):
        fx, fy = rand_cell()
        if [fx, fy] not in snake_list and not on_obstacle(fx, fy, obstacles):
            return fx, fy
    return rand_cell()

# ─────────────────────────────────────────────
#  RUN ONE LEVEL
# ─────────────────────────────────────────────
def run_level(level, total_score, high_score):
    """Returns (updated_total_score, advanced:bool)  advanced=False means death."""
    cfg = LEVEL_CONFIG[level - 1]
    speed, _, closed = cfg
    obstacles = generate_obstacles(cfg[1])

    x1, y1 = WIDTH // 2, HEIGHT // 2
    x1_change, y1_change = SNAKE_SIZE, 0
    snake_list = [[x1, y1]]
    length_of_snake = 1

    fx, fy = safe_food(snake_list, obstacles)
    bonus_food  = None
    bonus_timer = 0
    local_score = 0
    tick = 0
    particles.clear()

    while True:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                k = event.key
                if   k in (pygame.K_LEFT,  pygame.K_a) and x1_change == 0:
                    x1_change = -SNAKE_SIZE; y1_change = 0
                elif k in (pygame.K_RIGHT, pygame.K_d) and x1_change == 0:
                    x1_change =  SNAKE_SIZE; y1_change = 0
                elif k in (pygame.K_UP,    pygame.K_w) and y1_change == 0:
                    y1_change = -SNAKE_SIZE; x1_change = 0
                elif k in (pygame.K_DOWN,  pygame.K_s) and y1_change == 0:
                    y1_change =  SNAKE_SIZE; x1_change = 0
                elif k == pygame.K_p:   pause_screen()
                elif k == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        # Move
        x1 += x1_change
        y1 += y1_change

        # Wall logic
        if closed:
            if x1 < 0 or x1 >= WIDTH or y1 < 0 or y1 >= HEIGHT:
                spawn_particles(x1 % WIDTH, y1 % HEIGHT, C_FOOD, 30)
                return total_score + local_score, False
        else:
            x1 = x1 % WIDTH
            y1 = y1 % HEIGHT

        # Obstacle collision
        if on_obstacle(x1, y1, obstacles):
            spawn_particles(x1, y1, C_OBSTACLE, 30)
            return total_score + local_score, False

        # Update snake
        head = [x1, y1]
        snake_list.append(head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Self-collision
        if head in snake_list[:-1]:
            spawn_particles(x1, y1, C_SNAKE_H, 30)
            return total_score + local_score, False

        # Eat food
        if x1 == fx and y1 == fy:
            spawn_particles(fx, fy, C_FOOD, 18)
            length_of_snake += 1
            local_score += SCORE_PER_FOOD
            fx, fy = safe_food(snake_list, obstacles)
            if bonus_food is None and random.random() < BONUS_CHANCE:
                bx, by = safe_food(snake_list, obstacles)
                bonus_food  = [bx, by]
                bonus_timer = 200

        # Eat bonus food
        if bonus_food:
            bonus_timer -= 1
            if x1 == bonus_food[0] and y1 == bonus_food[1]:
                spawn_particles(bonus_food[0], bonus_food[1], C_FOOD2, 24)
                length_of_snake += 1
                local_score += BONUS_SCORE
                bonus_food = None
            elif bonus_timer <= 0:
                bonus_food = None

        cur_total = total_score + local_score
        if cur_total > high_score:
            high_score = cur_total

        # Draw
        draw_bg()
        draw_obstacles(obstacles)
        draw_food(fx, fy, tick)
        if bonus_food:
            draw_food(bonus_food[0], bonus_food[1], tick, bonus=True)

        for p in particles[:]:
            if not p.update(): particles.remove(p)
            else:              p.draw(screen)

        draw_snake(snake_list)
        draw_hud(cur_total, level, high_score, closed)

        # Level-up check
        if local_score >= LEVEL_UP_SCORE:
            if level < 10:
                # Flash "Level Up!"
                for _ in range(60):
                    pygame.event.pump()
                    draw_bg(); draw_obstacles(obstacles)
                    draw_snake(snake_list); draw_hud(cur_total, level, high_score, closed)
                    centered(f"LEVEL UP!  -->  {level+1}", font_large, C_GOLD, HEIGHT//2 - 30)
                    pygame.display.flip(); clock.tick(60)
                return cur_total, True   # advance
            else:
                # Won the game!
                for _ in range(90):
                    pygame.event.pump()
                    screen.fill(C_DARK)
                    centered("YOU  COMPLETED  ALL  10  LEVELS!", font_large, C_GOLD, HEIGHT//2 - 20)
                    pygame.display.flip(); clock.tick(60)
                return cur_total, True   # signal win

        pygame.display.flip()
        clock.tick(speed)
        tick += 1

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    high_score = 0

    while True:
        title_screen()

        score = 0
        level = 1
        alive = True

        while level <= 10 and alive:
            level_transition(level)
            score, alive = run_level(level, score, high_score)
            if score > high_score:
                high_score = score
            if alive:
                level += 1

        win    = alive and level > 10
        action = game_over_screen(score, high_score, min(level, 10), win=win)
        # "retry" loops back, "menu" also loops back (title shown again)

if __name__ == "__main__":
    main()
