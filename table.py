import pygame
import pymunk
import pymunk.pygame_util
import math
import numpy as np
from const import *
import random


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

class Ball:
    def __init__(self, x, y, color, space):
        self.color = color
        self.body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BALL_RADIUS))
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, BALL_RADIUS)
        self.shape.elasticity = ELASTICITY
        #self.shape.friction = 0.9
        self.pocketed = False
        space.add(self.body, self.shape)



class Table:
    def __init__(self, n):
        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        #self.space.damping = DAMPING
        self.create_walls()
        self.balls = []
        self.cue_ball = None
        self.num = n
        self.logging = None

    def close(self):
        for ball in self.balls:
            if ball.pocketed:
                continue
            self.space.remove(ball.body, ball.shape)

    def create_walls(self):
        """Creates the pool table walls with collisions."""
        self.static_lines = [
            pymunk.Segment(self.space.static_body, (30, 0), (610, 0), 1),
            pymunk.Segment(self.space.static_body, (660, 0), (1250, 0), 1),
            pymunk.Segment(self.space.static_body, (30, 640), (620, 640), 1),
            pymunk.Segment(self.space.static_body, (660, 640), (1250, 640), 1),
            pymunk.Segment(self.space.static_body, (0, 30), (0, 610), 1),
            pymunk.Segment(self.space.static_body, (1280, 30), (1280, 610), 1)
        ]
        for line in self.static_lines:
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
        for ball in self.balls:
            pygame.draw.circle(self.screen, ball.color, (int(ball.body.position.x), int(ball.body.position.y)), BALL_RADIUS)
        

    def apply_friction(self):
        """Applies friction to slow down balls based on v(t) = v0 - μgt."""
        for ball in self.balls:
            speed = ball.body.velocity.length
            if speed > 0:
                decay1 = MU * G * (1 / 60) 
                decay2 = ALPHA * speed * (1 / 60) 
                decay3 = BETA * speed ** 2 * (1 / 60)
                new_speed = max(0, speed - decay1 - decay2 - decay3)
                if new_speed == 0:
                    ball.body.velocity = (0, 0)
                else:
                    ball.body.velocity = ball.body.velocity.normalized() * new_speed

    def create_triangle(self):
        start_x = 900
        start_y = HEIGHT // 2
        for i in range(5):  
            for j in range(i + 1):
                x = start_x + i * (BALL_RADIUS * 2 + 1)
                y = start_y - i * (BALL_RADIUS + 0.5) + j * (BALL_RADIUS * 2 + 1)
                self.create_ball(x, y, WHITE)


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

    
    def new_render(self):
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

            self.space.step(1 / 60)
            self.apply_friction()

            if self.check_stop():
                self.check_pocketed()
                running = False

            pygame.display.flip()

            self.clock.tick(60)
        pygame.display.quit()
        pygame.quit()


    def make_shot_with_render(self, angle):
        """Applies a shot to the cue ball."""
        force = SHOOT_FORCE
        self.cue_ball.body.angular_velocity = 0
        self.cue_ball.body.apply_impulse_at_local_point((force * math.cos(angle * math.pi), force * math.sin(angle * math.pi)))
        self.new_render()


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
        self.cue_ball = Ball(positions[0][0], positions[0][1], RED, self.space)
        self.ball1 = Ball(positions[1][0], positions[1][1], WHITE, self.space)
        self.balls = [self.cue_ball, self.ball1]


    def generate_n_random(self, n):
        positions = []
        while len(positions) < n:
            x = random.randint(BALL_RADIUS + 30, WIDTH - BALL_RADIUS - 30)
            y = random.randint(BALL_RADIUS + 30, HEIGHT - BALL_RADIUS - 30)
            overlap = False
            for pos in positions:
                if math.hypot(x - pos[0], y - pos[1]) < BALL_RADIUS * 2:
                    overlap = True
                    break
            if not overlap:
                positions.append((x, y))
        for i in range(n):
            if i == 0:
                self.cue_ball = Ball(positions[i][0], positions[i][1], RED, self.space)
                self.balls.append(self.cue_ball)
            else:
                self.balls.append(Ball(positions[i][0], positions[i][1], WHITE, self.space))

    def respot_red(self):
        while True:
            x = random.randint(BALL_RADIUS + 30, WIDTH - BALL_RADIUS - 30)
            y = random.randint(BALL_RADIUS + 30, HEIGHT - BALL_RADIUS - 30)
            overlap = False
            for ball in self.balls:
                if math.hypot(x - ball.body.position.x, y - ball.body.position.y) < BALL_RADIUS * 2:
                    overlap = True
                    break
            if not overlap:
                self.cue_ball = Ball(x, y, RED, self.space)
                self.balls[0] = self.cue_ball
                break
        

    def check_stop(self):
        """Checks if all balls have stopped moving."""
        for ball in self.balls:
            if ball.body.velocity.length > 0:
                return False
        return True


    def check_pocketed(self):
        for ball in self.balls:
            if ball.pocketed:
                continue
            x, y = ball.body.position
            if is_point_outside_polygon((x, y), FIELD):
                if ball.color == RED:
                    self.logging["red_pocketed"] = True
                    self.space.remove(ball.body, ball.shape)
                    self.respot_red()
                    self.setup_collision_handlers()
                else:
                    self.logging["white_pocketed"] = True
                    ball.body.position = -100, -100
                    ball.pocketed = True
                    self.space.remove(ball.body, ball.shape)



    def make_shot(self, angle):
        """Applies a shot to the cue ball."""
        force = SHOOT_FORCE
        self.cue_ball.body.angular_velocity = 0
        self.cue_ball.body.apply_impulse_at_local_point((force * math.cos(angle*math.pi), force * math.sin(angle*math.pi)))
        self.reset_logging()
        running = True
        while running:
            self.space.step(1/60)
            self.apply_friction()
            if self.check_stop():
                running = False
        self.check_pocketed()



    def calculate_cue_pos(self):
        body = self.cue_ball.body
        x, y = body.position
        dists_to_pockets = []
        dists_to_balls = []
        angle_to_balls = []
        for pocket in POCKETS:
            dist = math.hypot(x - pocket[0], y - pocket[1])
            dists_to_pockets.append(dist)
        for ball in self.balls:
            if ball.color == RED:
                continue
            if ball.pocketed:
                dists_to_balls.append(-1)
                continue
            dist = math.hypot(x - ball.body.position.x, y - ball.body.position.y)
            dists_to_balls.append(dist)
        for ball in self.balls:
            if ball.color == RED:
                continue
            if ball.pocketed:
                angle_to_balls.append(-1)
                continue
            angle = math.atan2(ball.body.position.y - y, ball.body.position.x - x)
            angle_to_balls.append(angle)
        info = [x, y]
        info.extend(dists_to_pockets)
        info.extend(dists_to_balls)
        info.extend(angle_to_balls)
        return info


    def calculate_ball_pos(self):
        info = []
        for ball in self.balls:
            if ball.color == RED:
                continue
            if ball.pocketed:
                info.extend([-100, -100])
                info.extend([-1, -1, -1, -1, -1, -1])
                info.extend([-1, -1, -1, -1, -1, -1])
                continue
            x, y = ball.body.position
            info.extend([x, y])
            dists_to_pockets = []
            angles_to_pockets = []
            for pocket in POCKETS:
                dist = math.hypot(x - pocket[0], y - pocket[1])
                dists_to_pockets.append(dist)
                angle = math.atan2(pocket[1] - y, pocket[0] - x)
                angles_to_pockets.append(angle)
            info.extend(dists_to_pockets)
            info.extend(angles_to_pockets)
        return info

    
    def setup_collision_handlers(self):
        """Sets up collision handlers for tracking cue ball interactions."""
        def cue_hits_white(arbiter, space, data):
            """Triggered when the cue ball hits a white ball."""
            self.logging["white_hit"] = True
            if not self.logging["wall_hit"]:
                self.logging["white_before_wall"] = True
            return True  # Continue normal physics processing

        def cue_hits_wall(arbiter, space, data):
            """Triggered when the cue ball hits a wall."""
            self.logging["wall_hit"] = True
            return True  # Continue normal physics processing

        # Assign collision types
        self.cue_ball.shape.collision_type = 1  # Cue ball
        for ball in self.balls:
            if ball.color == WHITE:
                ball.shape.collision_type = 2  # White balls

        for wall in self.static_lines:
            wall.collision_type = 3  # Walls

        # Create collision handlers
        handler1 = self.space.add_collision_handler(1, 2)  # Cue ball - White ball
        handler1.begin = cue_hits_white  

        handler2 = self.space.add_collision_handler(1, 3)  # Cue ball - Wall
        handler2.begin = cue_hits_wall

    
    def reset_logging(self):
        self.logging = {
            "red_pocketed": False,
            "white_pocketed": False,
            "wall_hit": False,
            "white_hit": False,
            "white_before_wall": False,
        }

    def reset(self):
        """Resets the pool table."""
        for ball in self.balls:
            if not ball.pocketed:
                self.space.remove(ball.body, ball.shape)
        self.balls = []
        self.cue_ball = None
        self.reset_logging()
        self.generate_n_random(self.num)
        self.setup_collision_handlers()


    def get_observation(self):
        """Returns the observation of the environment."""
        #n = (2 + 6 + 2*(self.num_balls-1)) + 2*(self.num_balls-1) + 6*(self.num_balls-1) + 6*(self.num_balls-1)
        arr = []
        cue_info = self.calculate_cue_pos()
        ball_info = self.calculate_ball_pos()
        arr.extend(cue_info)
        arr.extend(ball_info)
        return np.array(arr, dtype=np.float32)


    def get_reward(self):
        """Returns the reward of the environment."""
        base = 0.5
        if self.logging["red_pocketed"]:
            base += -1
        if self.logging["white_pocketed"]:
            base += 50
        if self.logging["white_hit"]:
            if self.logging["white_before_wall"]:
                base += 10
            else:
                base += -1
        else:
            base += -2
        return base

    def is_done(self):
        """Returns if the episode is done."""
        pocketed_count = 0
        for ball in self.balls:
            if ball.pocketed and ball.color == WHITE:
                pocketed_count += 1
        if pocketed_count == self.num - 1:
            return True
        return False
        