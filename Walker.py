import random
import math
import numpy as np

from config import ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND, MAX_MOVES, MIDDLE_LINE_WEIGHT, MOVEMENT_LENGTH_LIMITER, SINK_STRENGTH, TORTUOUS_MOVEMENT_LENGTH_LIMITER, TORTUOUS_PROBABILITY, VECTOR_FIELD_WEIGHT, WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER, WALKER_CHILD_MAX_MOVES_MULTIPLIER, WALKER_CHILD_PATH_WIDTH_MULTIPLIER, WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER, WALKER_INITIAL_DEATH_PROBABILITY, WALKER_INITIAL_REPRODUCTION_PROBABILITY, WALKER_MATURITY_STEPS, WALKER_INITIAL_PATH_WIDTH, WALKER_PATH_WIDTH_DECAY
from util import add_vectors, bound, damped_sine, normalize_vector, rotate_vector

class Walker:
    def __init__(
            self, 
            grid,
            grid_size, 
            tortuous, 
            reproduction_probability, 
            death_probability, 
            initial_point = None, 
            source_point = None,
            initial_direction = None,
            width = None,
            moves = 0,
            max_moves = MAX_MOVES
        ):
        # Choose a random position on the SIZE x SIZE grid
        if initial_point is None:
            self.x = random.randint(0, grid_size - 1)
            self.y = random.randint(0, grid_size - 1)
        else:
            self.x, self.y = initial_point
        self.source_point = source_point        

        self.grid_size = grid_size
        self.grid = grid
        self.reproduction_probability = reproduction_probability
        self.death_probability = death_probability

        if initial_direction is not None:
            self.direction = initial_direction
        else:
            # Choose a random direction vector
            norm = 0.0
            while norm == 0.0:
                dir_x = random.randint(-1, 1)
                dir_y = random.randint(-1, 1)
                norm = np.sqrt(dir_x ** 2 + dir_y ** 2)
            self.direction = (dir_x/norm , dir_y/norm)

        if width is None:
            self.width = self.grid_size * WALKER_INITIAL_PATH_WIDTH
        else:
            self.width = width

        # Determine whether the walker has reached an edge
        self.dead = False

        self.tortuous = tortuous

        self.children = []

        self.moves = moves
        self.max_moves = max_moves

    def get_direction(self, point = None):
        if point is None:
            point = (self.x, self.y)
        x, y = point

        source_x, source_y = self.source_point
        sink_x, sink_y = (self.grid_size - source_x, self.grid_size - source_y)

        def E(q, r0, x, y):
            """Return the electric field vector E=(Ex,Ey) due to charge q at r0."""

            # If at source or sink, return a random vector
            if(r0[0] == x and r0[1] == y):
                return random.random(), random.random()

            den = np.hypot(x-r0[0], y-r0[1])**3
            return q * (x - r0[0]) / den, q * (y - r0[1]) / den

        ex, ey = E(1, (source_x, source_y), x, y)
        ex_, ey_ = E(-1 * SINK_STRENGTH, (sink_x, sink_y), x, y)

        vector_field_direction = normalize_vector((ex + ex_, ey + ey_))

        # self.paint_line(
        #     (source_x, source_y),
        #     (sink_x, sink_y)
        # )

        mid_x = (source_x + sink_x) / 2
        mid_y = (source_y + sink_y) / 2

        direction_towards_line = normalize_vector((mid_x - x, mid_y - y))

        return normalize_vector(
            add_vectors([
                (vector_field_direction, VECTOR_FIELD_WEIGHT),
                (direction_towards_line, MIDDLE_LINE_WEIGHT),
                (self.direction, None),
            ])
        )

    def move(self):
        for child in self.children:
            child.move()

        if self.dead:
            return False
        
        self.moves += 1

        tortuous_move = self.tortuous and random.random() <= TORTUOUS_PROBABILITY
        if tortuous_move:
            self.make_tortuous_move()
        else:
            self.make_normal_move()

        self.try_reproduce()
        self.try_die_old_age()
        return True
    
    def try_die_old_age(self):
        # if random.random() <= self.death_probability:
        #     self.dead = True
        if self.moves > self.max_moves:
            self.dead = True
        return

        # Death probability dependent on age (number of moves)
        death_prob = self.death_probability * (np.power(2, self.moves) / 500)
        death_prob = self.death_probability * (self.moves / 3)
        # death_prob = self.death_probability * (self.moves / 10)
        if random.random() <= death_prob:
            self.dead = True

    def check_bounds_and_die(self):
        if self.x >= self.grid_size - 1 or \
            self.y >= self.grid_size - 1 or \
            self.x <= 0 or \
            self.y <= 0:
            self.dead = True
    
    def try_reproduce(self):
        if self.moves < WALKER_MATURITY_STEPS:
            return
        ################# Remove later
        ################# Remove later
        ################# Remove later
        ################# Remove later
        ################# Remove later
        reproduction_prob = self.reproduction_probability
        if self.tortuous:
            reproduction_prob *= 0.75
        if random.random() < reproduction_prob:
            self.children.append(
                Walker(
                    self.grid, 
                    self.grid_size, 
                    self.tortuous,
                    self.reproduction_probability * WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER,
                    min(self.death_probability * WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER, 1.0),
                    (self.x, self.y),
                    self.source_point,
                    rotate_vector(self.direction, self.get_random_large_angle()),
                    self.width * WALKER_CHILD_PATH_WIDTH_MULTIPLIER,
                    self.moves,
                    self.max_moves * WALKER_CHILD_MAX_MOVES_MULTIPLIER
                )
            )
    
    def make_normal_move(self):
        self.make_small_move_straight()
        self.make_small_move_straight()
        self.make_small_move_straight()

    def make_small_move_straight(self):
        if self.dead:
            return
        turn_angle = self.get_random_small_angle()
        movement_length = self.get_random_small_movement_length()

        # Rotate the direction vector by TURN_ANGLE degrees
        self.direction = rotate_vector(self.get_direction(), turn_angle)

        final_pos_x = bound(self.grid_size, self.x + self.direction[0] * movement_length)
        final_pos_y = bound(self.grid_size, self.y + self.direction[1] * movement_length)

        # Move to that position and make all the points along the way 1
        stride_x = final_pos_x - self.x
        stride_y = final_pos_y - self.y

        NUM_STEPS = movement_length
        step_x = stride_x / NUM_STEPS
        step_y = stride_y / NUM_STEPS

        for _ in range(NUM_STEPS):
            self.x += step_x
            self.y += step_y
            self.paint_perpendicular((self.x, self.y), self.width)
            self.width_decay()
        
        self.check_bounds_and_die()

    def width_decay(self, decay=WALKER_PATH_WIDTH_DECAY):
        self.width *= (1 - decay)

    def make_tortuous_move(self):
        turn_angle = self.get_random_small_angle()
        self.direction = rotate_vector(self.get_direction(), turn_angle)

        amplitude = self.get_random_small_movement_length()
        wavelength = self.get_random_movement_length()
        self.make_sine_move(amplitude, wavelength)
        
    def make_sine_move(self, amplitude, wavelength):
        initial_x, initial_y = self.x, self.y
        total_angle = 360
        step_length = wavelength / total_angle
        penpendicular_direction = rotate_vector(self.direction, 90)
        for angle in range(1, total_angle + 1):
            base_x = initial_x + self.direction[0] * angle * step_length
            base_y = initial_y + self.direction[1] * angle * step_length

            self.x = base_x + damped_sine(angle, amplitude, t=self.moves) * penpendicular_direction[0]
            self.y = base_y + damped_sine(angle, amplitude, t=self.moves) * penpendicular_direction[1]
            
            self.paint_perpendicular((self.x, self.y), self.width)
            self.width_decay()
        self.check_bounds_and_die()

    def get_random_movement_length(self):
        dist = 0
        while dist == 0:
            dist = random.randint(1, math.floor((self.grid_size - 1) * MOVEMENT_LENGTH_LIMITER))
        return dist

    def get_random_small_movement_length(self):
        dist = 0
        while dist == 0:
            dist = math.floor(self.get_random_movement_length() * TORTUOUS_MOVEMENT_LENGTH_LIMITER)
        return dist
    
    def get_random_small_angle(self):
        return random.randint(-ANGLE_LOWER_BOUND, ANGLE_LOWER_BOUND)
    
    def get_random_large_angle(self):
        return np.random.choice(
            list(range(ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND)) + 
            list(range(-ANGLE_UPPER_BOUND, -ANGLE_LOWER_BOUND))
        )
    
    def paint_line(self, start_point, end_point):
        start_x, start_y = start_point
        end_x, end_y = end_point

        end_x = bound(self.grid_size, end_x)
        end_y = bound(self.grid_size, end_y)

        stride_x = end_x - start_x
        stride_y = end_y - start_y

        NUM_STEPS = math.ceil(np.sqrt(stride_x ** 2 + stride_y ** 2))
        step_x = stride_x / NUM_STEPS
        step_y = stride_y / NUM_STEPS

        for _ in range(NUM_STEPS):
            start_x += step_x
            start_y += step_y
            self.paint_point((start_x, start_y))

    def paint_point(self, point):
        x, y = point
        x, y = math.floor(x), math.floor(y)
        if x >= self.grid_size or \
            y >= self.grid_size or \
            x < 0 or \
            y < 0:
            return
        self.grid[x][y] = [255, 255, 255]
    
    def paint_perpendicular(self, point, width):
        x, y = point
        pendicular_positive_direction = rotate_vector(self.direction, 90)
        pendicular_negative_direction = rotate_vector(self.direction, -90)

        self.paint_line(
            (x, y),
            (
                x + pendicular_positive_direction[0] * width,
                y + pendicular_positive_direction[1] * width
            )
        )

        self.paint_line(
            (x, y),
            (
                x + pendicular_negative_direction[0] * width,
                y + pendicular_negative_direction[1] * width
            )
        )