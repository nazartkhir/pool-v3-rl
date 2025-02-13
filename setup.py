import pygame
import pymunk
import pymunk.pygame_util

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600  # Updated screen size
WIDTH, HEIGHT = 800, 400  # Pool table size
BALL_RADIUS = 10
X_SPACING = 0  # Adjusted spacing between balls on x-axis
Y_SPACING = 1  # Keep a small spacing on y-axis
FRICTION = 0.99

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pool Game")
clock = pygame.time.Clock()

# Create physics space
space = pymunk.Space()
space.gravity = (0, 0)

draw_options = pymunk.pygame_util.DrawOptions(screen)

balls = []
ball_colors = {}

def create_ball(x, y, color):
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BALL_RADIUS))
    body.position = x, y
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.elasticity = 0.9
    shape.friction = 0.8
    space.add(body, shape)
    balls.append((body, shape))
    ball_colors[body] = color  # Store color separately
    return body

# Create balls
cue_ball = create_ball(350, SCREEN_HEIGHT//2, RED)

start_x = 750  # Adjusted starting position for triangle formation
start_y = SCREEN_HEIGHT // 2
for i in range(5):  # Triangle formation
    for j in range(i + 1):
        x = start_x + i * (BALL_RADIUS * 2 + X_SPACING)
        y = start_y - i * (BALL_RADIUS + Y_SPACING/2) + j * (BALL_RADIUS * 2 + Y_SPACING)
        create_ball(x, y, WHITE)

def create_walls():
    static_lines = [
        pymunk.Segment(space.static_body, (200, 100), (1000, 100), 5),
        pymunk.Segment(space.static_body, (1000, 100), (1000, 500), 5),
        pymunk.Segment(space.static_body, (1000, 500), (200, 500), 5),
        pymunk.Segment(space.static_body, (200, 500), (200, 100), 5)
    ]
    for line in static_lines:
        line.elasticity = 0.9
        space.add(line)

def draw_walls():
    pygame.draw.line(screen, BROWN, (200, 100), (1000, 100), 5)
    pygame.draw.line(screen, BROWN, (1000, 100), (1000, 500), 5)
    pygame.draw.line(screen, BROWN, (1000, 500), (200, 500), 5)
    pygame.draw.line(screen, BROWN, (200, 500), (200, 100), 5)

create_walls()

def draw_balls():
    for body, shape in balls:
        pygame.draw.circle(screen, ball_colors[body], (int(body.position.x), int(body.position.y)), BALL_RADIUS)

running = True
while running:
    screen.fill(WHITE)  # Set background to white
    pygame.draw.rect(screen, GREEN, (200, 100, WIDTH, HEIGHT))  # Draw the pool table
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    space.step(1/60)
    draw_walls()
    draw_balls()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
