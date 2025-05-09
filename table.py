import pygame
import pymunk
import pymunk.pygame_util
import math
import numpy as np
import pymunk.util
from const import *
import random
import time

from pymunk import Vec2d


def point_to_segment_distance(seg_start, seg_end, point):
    seg_v = seg_end - seg_start
    pt_v = point - seg_start

    seg_len = seg_v.length
    seg_dir = seg_v.normalized() if seg_len != 0 else Vec2d(0, 0)

    proj = pt_v.dot(seg_dir)

    if proj < 0:
        closest = seg_start
    elif proj > seg_len:
        closest = seg_end
    else:
        closest = seg_start + proj * seg_dir

    return (point - closest).length


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
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        #self.space.collision_slop = 0.01
        #self.space.damping = DAMPING
        self.create_walls()
        self.balls = []
        self.cue_ball = None
        self.num = n
        self.logging = None
        self.time = 1

    def close(self):
        for ball in self.balls:
            if ball.pocketed:
                continue
            self.space.remove(ball.body, ball.shape)

    def create_walls(self):
        """Creates the pool table walls with collisions."""
        self.static_lines = [
            pymunk.Segment(self.space.static_body, (35, 0), (615, 0), 1),
            pymunk.Segment(self.space.static_body, (665, 0), (1245, 0), 1),
            pymunk.Segment(self.space.static_body, (35, 640), (615, 640), 1),
            pymunk.Segment(self.space.static_body, (665, 640), (1245, 640), 1),
            pymunk.Segment(self.space.static_body, (0, 35), (0, 605), 1),
            pymunk.Segment(self.space.static_body, (1280, 35), (1280, 605), 1)
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

        self.reset_logging()

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

            self.space.step(1 / 300)
            self.apply_friction()

            if self.check_stop():
                running = False

            pygame.display.flip()

            self.clock.tick(300)
        self.check_pocketed()
        pygame.display.quit()
        pygame.quit()


    def make_shot_with_render(self, action):
        """Applies a shot to the cue ball."""
        force = SHOOT_FORCE
        self.cue_ball.body.angular_velocity = 0
        angle = self.calc_angle(action)
        self.cue_ball.body.apply_impulse_at_local_point((force * math.cos(angle), force * math.sin(angle)))
        self.new_render()
        time.sleep(1)


    def generate_two_random(self):
        positions = []

        while len(positions) < 2:
            x = random.randint(BALL_RADIUS + 30, WIDTH - BALL_RADIUS - 30)
            y = random.randint(BALL_RADIUS + 30, HEIGHT - BALL_RADIUS - 30)
            overlap = False
            for pos in positions:
                if math.hypot(x - pos[0], y - pos[1]) < BALL_RADIUS * 2:
                    overlap = True
                    break
                
            if not overlap:
                positions.append((x, y))
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
                    #self.setup_collision_handlers()
                else:
                    self.logging["white_pocketed"] = True
                    ball.body.position = -100, -100
                    ball.pocketed = True
                    self.space.remove(ball.body, ball.shape)


    def calc_angle(self, action):
        """
        Calculates the angle of the shot using the corrected ghost ball offset (2*R)
        and aiming slightly inside the pocket for robustness. Uses Vec2d math.
        """
        num_pockets = len(POCKETS)
        num_target_balls = self.num - 1

        if num_target_balls <= 0:
             return 0.0
        ball_target_index = action // num_pockets
        pocket_index = action % num_pockets
        if not (0 <= ball_target_index < num_target_balls):
            return 0.0
        if not (0 <= pocket_index < num_pockets):
             return 0.0

        actual_ball_list_index = ball_target_index + 1
        if actual_ball_list_index >= len(self.balls):
             return 0.0

        target_ball = self.balls[actual_ball_list_index]

        if target_ball.pocketed:
            return 0.0 

        cue_pos = self.cue_ball.body.position
        target_pos = target_ball.body.position
        try:
            pocket_pos = pymunk.Vec2d(POCKETS[pocket_index][0], POCKETS[pocket_index][1])
        except IndexError:
             return 0.0

        vec_target_pocket = pocket_pos - target_pos
        dist_target_pocket = vec_target_pocket.length
        if dist_target_pocket < BALL_RADIUS:
             return 0.0
        try:
            dir_target_to_pocket_center = vec_target_pocket.normalized()
        except ZeroDivisionError:
             return 0.0

        adjustment_distance = BALL_RADIUS * 1
        adjusted_pocket_pos = pocket_pos - dir_target_to_pocket_center * adjustment_distance

        vec_target_adjusted_pocket = adjusted_pocket_pos - target_pos
        dist_target_adjusted_pocket = vec_target_adjusted_pocket.length

        if dist_target_adjusted_pocket < 1e-6:
             dir_to_pocket = dir_target_to_pocket_center
        else:
            try:
                 dir_to_pocket = vec_target_adjusted_pocket.normalized()
            except ZeroDivisionError:
                 dir_to_pocket = dir_target_to_pocket_center
        ghost_ball_offset = 2 * BALL_RADIUS
        ghost_ball_pos = target_pos - dir_to_pocket * ghost_ball_offset

        vec_cue_ghost = ghost_ball_pos - cue_pos
        angle = vec_cue_ghost.angle
        return angle


    def make_shot(self, action):
        """Applies a shot to the cue ball."""
        force = SHOOT_FORCE
        self.cue_ball.body.angular_velocity = 0
        for ball in self.balls:
            ball.body.angular_velocity = 0
        angle = self.calc_angle(action)
        self.cue_ball.body.apply_impulse_at_local_point((force * math.cos(angle), force * math.sin(angle)))
        self.reset_logging()
        running = True
        while running:
            self.space.step(1/300)
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
    

    def get_straightness(self, action):
        """
        Calculates the straightness of a potential shot (cue-target-pocket alignment).
        """
        num_pockets = len(POCKETS)
        num_target_balls = self.num - 1

        if num_target_balls <= 0:
            return -1.0
        ball_target_index = action // num_pockets
        pocket_index = action % num_pockets

        if not (0 <= ball_target_index < num_target_balls):
            return -1.0
        if not (0 <= pocket_index < num_pockets):
             return -1.0
        actual_ball_list_index = ball_target_index + 1
        if actual_ball_list_index >= len(self.balls):
             return -1.0

        target_ball = self.balls[actual_ball_list_index]

        if target_ball.pocketed:
            return -1.0 

        cue_pos = self.cue_ball.body.position
        target_pos = target_ball.body.position
        try:
            pocket_pos = pymunk.Vec2d(POCKETS[pocket_index][0], POCKETS[pocket_index][1])
        except IndexError:
             return -1.0
        vec_target_cue = cue_pos - target_pos
        vec_target_pocket = pocket_pos - target_pos

        mag_tc = vec_target_cue.length
        mag_tp = vec_target_pocket.length
        min_dist = 0.1 * BALL_RADIUS
        if mag_tc < min_dist or mag_tp < min_dist:
            return -1.0
        dot_product = vec_target_cue.dot(vec_target_pocket)
        cos_theta = max(-1.0, min(1.0, dot_product / (mag_tc * mag_tp)))
        angle_ctp_rad = math.acos(cos_theta)
        straightness_value = (2.0 * angle_ctp_rad / math.pi) - 1.0
        if straightness_value < 0:
            return -1
        impossible_threshold_rad = math.radians(1)
        if angle_ctp_rad < impossible_threshold_rad:
            return -1.0

        return straightness_value
    

    def calculate_straightness(self):
        """
        Calculates the straightness value for all possible actions.
        """
        num_actions = (self.num - 1) * len(POCKETS)
        straightness_values = np.full(num_actions, -1.0, dtype=np.float32)

        for action in range(num_actions):
            straightness = self.get_straightness(action)
            straightness_values[action] = straightness

        return straightness_values
    
    def is_pot_possible(self, action):
        """
        Determines if a shot is physically possible, primarily checking for obstructions.
        This now includes checking the path from the target ball to the pocket.
        """     
        num_pockets = len(POCKETS)
        num_target_balls = self.num - 1     
        if num_target_balls <= 0:
            return 0       
        ball_target_index = action // num_pockets
        pocket_index = action % num_pockets     
        if not (0 <= ball_target_index < num_target_balls):
            return 0
        if not (0 <= pocket_index < num_pockets):
            return 0        
        actual_ball_list_index = ball_target_index + 1
        if actual_ball_list_index >= len(self.balls):
            return 0        
        target_ball = self.balls[actual_ball_list_index]        
        if target_ball.pocketed:
            return 0       
        cue_pos = self.cue_ball.body.position
        target_pos = target_ball.body.position
        pocket_pos = pymunk.Vec2d(*POCKETS[pocket_index])       
        if cue_pos.get_distance(target_pos) < 1e-6:
            return 0        
        shot_line = (cue_pos, target_pos)
        for other_ball in self.balls:
            if other_ball in [self.cue_ball, target_ball] or other_ball.pocketed:
                continue
            other_ball_pos = other_ball.body.position
            dist_to_shot_line = point_to_segment_distance(shot_line[0], shot_line[1], other_ball_pos)
            if dist_to_shot_line < 2 * BALL_RADIUS:
                direction = target_pos - cue_pos
                proj_len = (other_ball_pos - cue_pos).dot(direction.normalized())
                if 0 < proj_len < direction.length:
                    return 0        
        pocket_line = (target_pos, pocket_pos)
        for other_ball in self.balls:
            if other_ball in [self.cue_ball, target_ball] or other_ball.pocketed:
                continue
            other_ball_pos = other_ball.body.position
            dist_to_pocket_line = point_to_segment_distance(pocket_line[0], pocket_line[1], other_ball_pos)
            if dist_to_pocket_line < 2 * BALL_RADIUS:
                direction = pocket_pos - target_pos
                proj_len = (other_ball_pos - target_pos).dot(direction.normalized())
                if 0 < proj_len < direction.length:
                    return 0        
        return 1        

    

    def calculate_possibility(self):
        num_actions = (self.num - 1) * len(POCKETS)
        pos_values = np.full(num_actions, 0, dtype=np.float32)

        for action in range(num_actions):
            pos = self.is_pot_possible(action)
            pos_values[action] = pos

        return pos_values

    
    def setup_collision_handlers(self):
        """Sets up collision handlers for tracking cue ball interactions."""
        def cue_hits_white(arbiter, space, data):
            """Triggered when the cue ball hits a white ball."""
            self.logging["white_hit"] = True
            if not self.logging["wall_hit"]:
                self.logging["white_before_wall"] = True
            return True

        def cue_hits_wall(arbiter, space, data):
            """Triggered when the cue ball hits a wall."""
            self.logging["wall_hit"] = True
            return True

        self.cue_ball.shape.collision_type = 1
        for ball in self.balls:
            if ball.color == WHITE:
                ball.shape.collision_type = 2

        for wall in self.static_lines:
            wall.collision_type = 3

        handler1 = self.space.add_collision_handler(1, 2)
        handler1.begin = cue_hits_white  

        handler2 = self.space.add_collision_handler(1, 3)
        handler2.begin = cue_hits_wall

    
    def reset_logging(self):
        self.logging = {
            "red_pocketed": False,
            "white_pocketed": False,
            "num_pocketed": 0,
        }


    def reset(self):
        """Resets the pool table."""
        for ball in self.balls:
            if not ball.pocketed:
                self.space.remove(ball.body, ball.shape)
        self.balls = []
        self.time = 1
        self.cue_ball = None
        self.reset_logging()
        self.generate_n_random(self.num)
        #self.setup_collision_handlers()


    def get_time(self):
        """Returns the time since the last reset."""
        return self.time

    def get_observation(self):
        """Returns the observation of the environment."""
        #n = (2 + 6 + 2*(self.num_balls-1)) + 2*(self.num_balls-1) + 6*(self.num_balls-1) + 6*(self.num_balls-1)
        arr = []
        time = self.get_time()
        cue_info = self.calculate_cue_pos()
        ball_info = self.calculate_ball_pos()
        str_info = self.calculate_straightness()
        pos_info = self.calculate_possibility()
        arr.append(time)
        arr.extend(cue_info)
        arr.extend(ball_info)
        arr.extend(str_info)
        arr.extend(pos_info)
        return np.array(arr, dtype=np.float32)


    def get_reward(self):
        """Returns the reward of the environment."""
        base = 0
        time = self.get_time()
        if self.logging["red_pocketed"]:
            base += -10
        if self.logging["white_pocketed"]:
            self.logging["num_pocketed"] += 1
            base += 100*self.logging["num_pocketed"]
            time = 1
        else:
            self.logging["num_pocketed"] = 0
            base -= time
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
        
