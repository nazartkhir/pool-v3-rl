import pygame
import pymunk
import pymunk.pygame_util
import math

# Initialize pygame
pygame.init()


WIDTH, HEIGHT = 1280, 640
BALL_RADIUS = 15
SPEED_THRESHOLD = 15
SHOOT_FORCE = 1000

FIELD = [(30,0), (1250,0), (1280, 30), (1280, 610), (1250, 640), (30, 640), (0, 610), (0, 30)]


WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)


# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pool Game")
clock = pygame.time.Clock()

# Create physics space
space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.85

draw_options = pymunk.pygame_util.DrawOptions(screen)
font = pygame.font.Font(None, 36)

balls = []
ball_colors = {}

def create_ball(x, y, color):
    """Creates a billiard ball with given position and color."""
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BALL_RADIUS))
    body.position = x, y
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.elasticity = 0.9
    shape.friction = 0.9
    space.add(body, shape)
    balls.append((body, shape))
    ball_colors[body] = color
    return body

# Create cue ball (Red ball that can be shot)
cue_ball = create_ball(300, 400, RED)

# Create triangle formation of balls
start_x = 900
start_y = HEIGHT // 2
for i in range(5):  
    for j in range(i + 1):
        x = start_x + i * (BALL_RADIUS * 2 + 1)
        y = start_y - i * (BALL_RADIUS + 0.5) + j * (BALL_RADIUS * 2 + 1)
        create_ball(x, y, WHITE)

def create_walls():
    """Creates the pool table walls with collisions."""
    static_lines = [
        pymunk.Segment(space.static_body, (30, 0), (610, 0), 1),
        pymunk.Segment(space.static_body, (660, 0), (1250, 0), 1),
        pymunk.Segment(space.static_body, (30, 640), (620, 640), 1),
        pymunk.Segment(space.static_body, (660, 640), (1250, 640), 1),
        pymunk.Segment(space.static_body, (0, 30), (0, 610), 1),
        pymunk.Segment(space.static_body, (1280, 30), (1280, 610), 1)
    ]
    for line in static_lines:
        line.elasticity = 0.7
        space.add(line)

create_walls()

def draw_walls():
    """Draws the pool table walls."""
    pygame.draw.line(screen, BROWN, (30, 0), (620, 0), 5)
    pygame.draw.line(screen, BROWN, (660, 0), (1250, 0), 5)
    pygame.draw.line(screen, BROWN, (30, 640), (620, 640), 5)
    pygame.draw.line(screen, BROWN, (660, 640), (1250, 640), 5)
    pygame.draw.line(screen, BROWN, (0, 30), (0, 610), 5)
    pygame.draw.line(screen, BROWN, (1280, 30), (1280, 610), 5)


def draw_pockets():
    """Draws the pockets on the pool table."""
    pygame.draw.line(screen, BLACK, (0, 30), (30, 0), 5)
    pygame.draw.line(screen, BLACK, (1250, 0), (1280, 30), 5)
    pygame.draw.line(screen, BLACK, (0, 610), (30, 640), 5)
    pygame.draw.line(screen, BLACK, (1250, 640), (1280, 610), 5)
    pygame.draw.line(screen, BLACK, (620, 0), (660, 0), 5)
    pygame.draw.line(screen, BLACK, (620, 640), (660, 640), 5)


def draw_balls():
    """Draws all balls on the screen."""
    for body, shape in balls:
        pygame.draw.circle(screen, ball_colors[body], (int(body.position.x), int(body.position.y)), BALL_RADIUS)

def apply_friction():
    """Stops balls that have very low speed."""
    for body, shape in balls:
        speed = body.velocity.length
        if speed < SPEED_THRESHOLD:
            body.velocity = (0, 0)

def draw_aim_arrow():
    """Draws the aiming arrow for the cue ball."""
    arrow_length = 100
    end_x = cue_ball.position.x + arrow_length * math.cos(aim_angle)
    end_y = cue_ball.position.y + arrow_length * math.sin(aim_angle)
    pygame.draw.line(screen, BLACK, (cue_ball.position.x, cue_ball.position.y), (end_x, end_y), 3)
    pygame.draw.circle(screen, BLACK, (int(end_x), int(end_y)), 5)


def is_point_outside_polygon(point, vertices):
    """Checks if a point is outside a given polygon using the Ray Casting method."""
    x, y = point
    inside = False
    n = len(vertices)
    
    px, py = vertices[0]
    for i in range(n + 1):
        sx, sy = vertices[i % n]
        if min(py, sy) < y <= max(py, sy) and x <= max(px, sx):
            if py != sy:
                xinters = (y - py) * (sx - px) / (sy - py) + px
            if px == sx or x <= xinters:
                inside = not inside
        px, py = sx, sy

    return not inside 


def check_pocket():
    for body, shape in balls:
        x, y = body.position
        if is_point_outside_polygon((x, y), FIELD):
            space.remove(body, shape)
            balls.remove((body, shape))
            del ball_colors[body]



aim_mode = False
aim_angle = 0

running = True

while running:
    cue_ball.angular_velocity = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                aim_angle = 0
                aim_mode = True  # Start aiming
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s and aim_mode:
                # Shoot the cue ball
                force_x = SHOOT_FORCE * math.cos(aim_angle)
                force_y = SHOOT_FORCE * math.sin(aim_angle)
                cue_ball.apply_impulse_at_local_point((force_x, force_y))
                aim_mode = False  # Stop aiming

    keys = pygame.key.get_pressed()
    if aim_mode:
        if keys[pygame.K_LEFT]:
            aim_angle -= 0.02  # Rotate counter-clockwise
        if keys[pygame.K_RIGHT]:
            aim_angle += 0.02  # Rotate clockwise

    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))
    
    draw_pockets()
    draw_walls()
    

    space.step(1/60)
    apply_friction()
    draw_balls()

    check_pocket()

    if aim_mode:
        draw_aim_arrow()

    pygame.display.flip()
    clock.tick(180)
