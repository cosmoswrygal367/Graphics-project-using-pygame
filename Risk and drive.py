import pygame
import random

pygame.init()

# --------- Screen Setup ----------
WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Risk Drive")
clock = pygame.time.Clock()
FPS = 60

# --------- Colors ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 150)  # All obstacles same color
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
ROAD_GRAY = (105, 105, 105)
GREEN = (0, 255, 0)

# --------- Player ----------
car_width, car_height = 60, 20
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - 120
car_speed = 7

lives = 3
score = 0
max_lives = 3

# --------- Road ----------
road_x = 200
road_width = 600

# --------- Coins ----------
num_points = 5
points = [{'x': random.randint(road_x + 10, road_x + road_width - 10), 
           'y': random.randint(-900, 0), 'speed': 5} for _ in range(num_points)]

# --------- Obstacles ----------
obstacles = [
    {'x': random.randint(road_x, road_x + road_width - 120), 'y': random.randint(-600, 0),
     'w': 120, 'h': 40, 'real': True, 'split': False},
    {'x': random.randint(road_x, road_x + road_width - 60), 'y': random.randint(-600, 0),
     'w': 60, 'h': 40, 'real': False, 'split': False},
    {'x': random.randint(road_x, road_x + road_width - 60), 'y': random.randint(-600, 0),
     'w': 60, 'h': 40, 'real': False, 'split': False},
]

# --------- Life boosters (hearts) ----------
hearts = []

# --------- Lamps ----------
lamps = [{'x': road_x - 50, 'y': y} for y in range(0, HEIGHT, 150)] + \
        [{'x': road_x + road_width + 20, 'y': y} for y in range(0, HEIGHT, 150)]

game_over = False

# --------- Functions ----------
def draw_road():
    pygame.draw.rect(screen, ROAD_GRAY, (road_x, 0, road_width, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (road_x + road_width // 2 - 5, i, 10, 20))

def draw_car(x, y):
    pygame.draw.rect(screen, RED, (x, y, car_width, car_height))
    pygame.draw.rect(screen, RED, (x + 15, y - 15, 30, 15))  # roof
    pygame.draw.circle(screen, BLACK, (x + 15, y + car_height), 10)
    pygame.draw.circle(screen, BLACK, (x + 45, y + car_height), 10)

def draw_coin(x, y):
    pygame.draw.circle(screen, YELLOW, (x, y), 8)
    pygame.draw.circle(screen, (255, 255, 150), (x, y), 4)

def draw_heart(x, y):
    pygame.draw.circle(screen, RED, (x - 5, y), 6)
    pygame.draw.circle(screen, RED, (x + 5, y), 6)
    pygame.draw.polygon(screen, RED, [(x - 10, y), (x + 10, y), (x, y + 12)])

def draw_obstacle(ob):
    pygame.draw.rect(screen, GRAY, (ob['x'], ob['y'], ob['w'], ob['h']))
    # Optional: small line to hint splitting
    if ob['w'] > 60:
        pygame.draw.line(screen, WHITE, (ob['x'] + ob['w']//2, ob['y']), 
                         (ob['x'] + ob['w']//2, ob['y'] + ob['h']), 2)

def draw_lamp(lamp):
    pygame.draw.line(screen, BLACK, (lamp['x'], lamp['y']), (lamp['x'], lamp['y'] + 50), 4)
    pygame.draw.circle(screen, YELLOW, (lamp['x'], lamp['y']), 7)

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# --------- Game Loop ----------
running = True
while running:
    clock.tick(FPS)
    screen.fill(ORANGE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Keys ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > road_x:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < road_x + road_width - car_width:
        car_x += car_speed

    # --- Draw road & lamps ---
    draw_road()
    for lamp in lamps:
        draw_lamp(lamp)

    # --- Update coins ---
    for point in points:
        point['y'] += point['speed']
        if point['y'] > HEIGHT:
            point['y'] = random.randint(-900, 0)
            point['x'] = random.randint(road_x + 10, road_x + road_width - 10)
        draw_coin(point['x'], point['y'])
        if check_collision(pygame.Rect(car_x, car_y, car_width, car_height),
                           pygame.Rect(point['x'] - 8, point['y'] - 8, 16, 16)):
            score += 1
            point['y'] = random.randint(-900, 0)
            point['x'] = random.randint(road_x + 10, road_x + road_width - 10)

    # --- Update obstacles ---
    for ob in obstacles:
        ob['y'] += 5

        # Split dynamically if width > 60 and player is close
        if ob['w'] > 60 and car_y < ob['y'] + ob['h'] + 50:
            if not ob['split'] and random.random() < 0.03:
                ob1 = {'x': ob['x'], 'y': ob['y'], 'w': ob['w']//2, 'h': ob['h'], 'real': ob['real'], 'split': True}
                ob2 = {'x': ob['x'] + ob['w']//2, 'y': ob['y'], 'w': ob['w']//2, 'h': ob['h'], 'real': ob['real'], 'split': True}
                obstacles.append(ob1)
                obstacles.append(ob2)
                obstacles.remove(ob)
                continue

        if ob['y'] > HEIGHT:
            ob['y'] = random.randint(-600, 0)
            ob['x'] = random.randint(road_x, road_x + road_width - ob['w'])
            ob['split'] = False

        draw_obstacle(ob)

        if check_collision(pygame.Rect(car_x, car_y, car_width, car_height),
                           pygame.Rect(ob['x'], ob['y'], ob['w'], ob['h'])):
            if ob['real']:
                lives -= 1
                if random.random() < 0.5:
                    hearts.append({'x': random.randint(road_x + 10, road_x + road_width - 10),
                                   'y': -50})
            obstacles.remove(ob)
            new_ob = {'x': random.randint(road_x, road_x + road_width - 120 if random.random()<0.5 else road_x + road_width - 60),
                      'y': random.randint(-600, 0),
                      'w': 120 if random.random()<0.5 else 60,
                      'h': 40,
                      'real': random.choice([True, False]),
                      'split': False}
            obstacles.append(new_ob)
            if lives <= 0:
                game_over = True

    # --- Update hearts ---
    for heart in hearts[:]:
        heart['y'] += 5
        draw_heart(heart['x'], heart['y'])
        if check_collision(pygame.Rect(car_x, car_y, car_width, car_height),
                           pygame.Rect(heart['x'] - 10, heart['y'] - 10, 20, 20)):
            if lives < max_lives:
                lives += 1
            hearts.remove(heart)

    # --- Draw car ---
    draw_car(car_x, car_y)

    # --- HUD ---
    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))

    # --- Game Over ---
    if game_over:
        over_font = pygame.font.SysFont(None, 72)
        over_text = over_font.render("GAME OVER", True, RED)
        score_text = over_font.render(f"Your Final Score: {score}", True, BLACK)
        screen.blit(over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - 200, HEIGHT // 2 + 30))

    pygame.display.update()

pygame.quit()
