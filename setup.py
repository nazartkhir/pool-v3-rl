import pygame
import pymunk
import pymunk.pygame_util
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 640  # Pool table size
BALL_RADIUS = 15
FRICTION = 0.99
SPEED_THRESHOLD = 10  # Speed threshold for stopping balls


# Colors
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
space.damping = 0.8  # Simulate friction

draw_options = pymunk.pygame_util.DrawOptions(screen)

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
        line.elasticity = 0.5
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
        speed = body.velocity.length  # Get current speed
        if speed < SPEED_THRESHOLD:
            body.velocity = (0, 0)  # Stop the ball completely


def shoot_ball():
    """Handles the shooting mechanic of the cue ball (red ball)."""
    global is_angle_set, is_force_set, angle, force
    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
    
    # Find the direction vector from the cue ball to the mouse position
    direction_x = mouse_x - cue_ball.position.x
    direction_y = mouse_y - cue_ball.position.y
    
    # Calculate the distance (force) of the shot, which will be based on how far the mouse is dragged
    distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
    
    # Normalize the direction vector to apply the force to the cue ball in the correct direction
    if distance > 0:
        direction_x /= distance
        direction_y /= distance
    
    # The force can be scaled by the distance, for example, 1:1 scaling
    force = min(distance * 1.5, 1000)  # Cap the force to a reasonable value
    
    # Set the angle (direction) of the shot
    angle = math.atan2(direction_y, direction_x)
    
    # Apply the force to the cue ball in the calculated direction
    cue_ball.velocity = (direction_x * force, direction_y * force)
    
    # Reset flags so we don't drag the ball after the shot
    is_angle_set = True
    is_force_set = True

def handle_drag_and_shoot():
    """Handles the dragging and shooting of the red cue ball."""
    global is_angle_set, angle_slider_pos, force_slider_pos
    
    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get current mouse position
    
    if pygame.mouse.get_pressed()[0]:  # If left mouse button is held down
        # If the mouse is pressed over the cue ball, allow dragging
        if pygame.mouse.get_pressed()[0] and cue_ball.position.get_distance((mouse_x, mouse_y)) < BALL_RADIUS:
            cue_ball.position = mouse_x, mouse_y  # Move cue ball to the mouse position
            is_angle_set = False  # Do not shoot yet
            is_force_set = False  # Do not apply force yet
    
    elif pygame.mouse.get_pressed()[0] == 0 and not is_angle_set:  # If mouse button is released
        # Shoot the ball once the mouse is released
        shoot_ball()

# Variables for controlling the shot
angle = 0  # Initial angle
force = 500  # Default force (can be adjusted with slider)
is_angle_set = False  # Flag to check if angle is set
is_force_set = False  # Flag to check if force is set
angle_slider_pos = 0  # Initial angle slider position (0 to 360)
force_slider_pos = 500  # Initial force slider position (0 to 1000)

font = pygame.font.Font(None, 36)

while True:
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))
    
    draw_pockets()
    draw_walls()
    
    #handle_drag_and_shoot()

    space.step(1/60)
    apply_friction()
    draw_balls()

    pygame.display.flip()
    clock.tick(60)
