import pygame
import pymunk
import pymunk.pygame_util
import math
import numpy as np
from const import *
import random


class Table:
    def __init__(self):
        
        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = DAMPING
        self.create_walls()
        self.balls = []
        self.ball_colors = {}
        self.potted = []
        self.cue_ball = None

    def close(self):
        for body, shape in self.balls:
            self.space.remove(body, shape)
        self.balls = []
        self.ball_colors = {}
    
    def create_ball(self, x,y, color):
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BALL_RADIUS))
        body.position = x, y
        shape = pymunk.Circle(body, BALL_RADIUS)
        shape.elasticity = 0.9
        shape.friction = 0.9
        self.space.add(body, shape)
        self.balls.append((body, shape))
        self.potted.append(False)
        self.ball_colors[body] = color
        return body

    def create_walls(self):
        """Creates the pool table walls with collisions."""
        static_lines = [
            pymunk.Segment(self.space.static_body, (30, 0), (610, 0), 1),
            pymunk.Segment(self.space.static_body, (660, 0), (1250, 0), 1),
            pymunk.Segment(self.space.static_body, (30, 640), (620, 640), 1),
            pymunk.Segment(self.space.static_body, (660, 640), (1250, 640), 1),
            pymunk.Segment(self.space.static_body, (0, 30), (0, 610), 1),
            pymunk.Segment(self.space.static_body, (1280, 30), (1280, 610), 1)
        ]
        for line in static_lines:
            line.elasticity = 0.7
            self.space.add(line)


    def draw_walls(self):
        """Draws the pool table walls."""
        pygame.draw.line(self.screen, BROWN, (30, 0), (620, 0), 5)
        pygame.draw.line(self.screen, BROWN, (660, 0), (1250, 0), 5)
        pygame.draw.line(self.screen, BROWN, (30, 640), (620, 640), 5)
        pygame.draw.line(self.screen, BROWN, (660, 640), (1250, 640), 5)
        pygame.draw.line(self.screen, BROWN, (0, 30), (0, 610), 5)
        pygame.draw.line(self.screen, BROWN, (1280, 30), (1280, 610), 5)


    def draw_pockets(self):
        """Draws the pockets on the pool table."""
        pygame.draw.line(self.screen, BLACK, (0, 30), (30, 0), 5)
        pygame.draw.line(self.screen, BLACK, (1250, 0), (1280, 30), 5)
        pygame.draw.line(self.screen, BLACK, (0, 610), (30, 640), 5)
        pygame.draw.line(self.screen, BLACK, (1250, 640), (1280, 610), 5)
        pygame.draw.line(self.screen, BLACK, (620, 0), (660, 0), 5)
        pygame.draw.line(self.screen, BLACK, (620, 640), (660, 640), 5)


    def draw_balls(self):
        """Draws all balls on the screen."""
        for body, shape in self.balls:
            pygame.draw.circle(self.screen, self.ball_colors[body], (int(body.position.x), int(body.position.y)), BALL_RADIUS)

    def apply_friction(self):
        """Stops balls that have very low speed."""
        for body, shape in self.balls:
            speed = body.velocity.length
            if speed < SPEED_THRESHOLD:
                body.velocity = (0, 0)

    def create_triangle(self):
        start_x = 900
        start_y = HEIGHT // 2
        for i in range(5):  
            for j in range(i + 1):
                x = start_x + i * (BALL_RADIUS * 2 + 1)
                y = start_y - i * (BALL_RADIUS + 0.5) + j * (BALL_RADIUS * 2 + 1)
                self.create_ball(x, y, WHITE)


    def is_point_outside_polygon(self, point, vertices):
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


    def check_pocket(self):
        self.flag = 0
        for body, shape in self.balls:
            x, y = body.position
            if self.is_point_outside_polygon((x, y), FIELD) and not self.potted[self.balls.index((body, shape))]:
                self.space.remove(body, shape)
                self.potted[self.balls.index((body, shape))] = True
                body.position = -100, -100
                color = self.ball_colors[body]
                if color == WHITE:
                    self.flag = 1
                if color == RED:
                    self.flag = 2

    def render(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pool Game")
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.font = pygame.font.Font(None, 36)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.screen.fill(WHITE)
            pygame.draw.rect(self.screen, GREEN, (0, 0, WIDTH, HEIGHT))

            self.draw_pockets()
            self.draw_walls()
            self.draw_balls()
            
            pygame.display.flip()
            self.clock.tick(60)
        pygame.display.quit()
        pygame.quit()

    def generate_two_balls(self):
        """Generates two balls on the pool table."""
        self.cue_ball = self.create_ball(300, 300, RED)
        self.create_ball(500, 300, WHITE)

    def generate_two_random(self):
        positions = []

        while len(positions) < 2:
            x = random.randint(BALL_RADIUS + 30, WIDTH - BALL_RADIUS - 30)
            y = random.randint(BALL_RADIUS + 30, HEIGHT - BALL_RADIUS - 30)

            # Check for overlap with existing balls
            overlap = False
            for pos in positions:
                if math.hypot(x - pos[0], y - pos[1]) < BALL_RADIUS * 2:
                    overlap = True
                    break
                
            if not overlap:
                positions.append((x, y))

        # Create balls at the random positions
        self.cue_ball = self.create_ball(positions[0][0], positions[0][1], RED)
        self.create_ball(positions[1][0], positions[1][1], WHITE)



    def check_stop(self):
        """Checks if all balls have stopped moving."""
        for body, shape in self.balls:
            if body.velocity.length > SPEED_THRESHOLD:
                return False
        return True



    def make_shot(self, angle):
        """Applies a shot to the cue ball."""
        force = SHOOT_FORCE
        self.cue_ball.angular_velocity = 0
        self.cue_ball.apply_impulse_at_local_point((force * math.cos(angle*math.pi), force * math.sin(angle*math.pi)))
        running = True
        while running:
            self.space.step(1/60)
            self.apply_friction()
            if self.check_stop():
                running = False
        self.check_pocket()
            

    def get_balls_cords(self):
        """Returns the coordinates of all balls."""
        balls = [body.position for body, shape in self.balls]
        final = []
        for ball in balls:
            final.append(ball.x)
            final.append(ball.y)
        return final
    
    def reset(self):
        """Resets the pool table."""
        for body, shape in self.balls:
            if not self.potted[self.balls.index((body, shape))]:
                self.space.remove(body, shape)
        self.balls = []
        self.ball_colors = {}
        self.potted = []
        self.generate_two_balls()
    
    def get_observation(self):
        """Returns the observation of the environment."""
        return np.array(self.get_balls_cords(), dtype=np.float32)
    
    def get_reward(self):
        """Returns the reward of the environment."""
        if self.flag == 1:
            return 1
        if self.flag == 2:
            return -0.2
        return -0.001

    def is_done(self):
        """Returns if the episode is done."""
        return self.potted.count(True) == 1