import random
import math
import numpy as np

from config import ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND, MOVEMENT_LENGTH_LIMITER, TORTUOUS_MOVEMENT_LENGTH_LIMITER, WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER, WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER, WALKER_INITIAL_DEATH_PROBABILITY, WALKER_INITIAL_REPRODUCTION_PROBABILITY, WALKER_MATURITY_STEPS
from util import bound, rotate_vector

class Walker:
    def __init__(
            self, 
            grid,
            grid_size, 
            tortuous, 
            tortuousity_probability, 
            reproduction_probability, 
            death_probability, 
            initial_point = None, 
            initial_direction = None
        ):
        # Choose a random position on the SIZE x SIZE grid
        if initial_point is None:
            self.x = random.randint(0, grid_size - 1)
            self.y = random.randint(0, grid_size - 1)
        else:
            self.x, self.y = initial_point

        self.points = [(self.x, self.y)]
        self.turn_angles = []

        self.grid_size = grid_size
        self.grid = grid
        self.tortuousity_probability = tortuousity_probability
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

        # Determine whether the walker has reached an edge
        self.dead = False

        self.tortuous = tortuous
        self.tortuous_points = []

        self.children = []
    
    def move(self):
        for child in self.children:
            child.move()

        if self.dead:
            return False

        # Make a large turn based on the TURN_PROBABILITY
        tortuous_turn = random.random() <= self.tortuousity_probability and \
                        self.tortuous

        if tortuous_turn:
            self.make_tortuous_move()
        else:
            self.make_move(
                self.get_random_small_angle(),
                self.get_random_movement_length()
            )

        self.try_reproduce()
        self.try_die()
        return True
    
    def try_die(self):
        if random.random() <= self.death_probability:
            self.dead = True

    def check_bounds_and_die(self):
        if self.x >= self.grid_size - 1 or \
            self.y >= self.grid_size - 1 or \
            self.x <= 0 or \
            self.y <= 0:
            self.dead = True
    
    def try_reproduce(self):
        if len(self.points) < WALKER_MATURITY_STEPS:
            return
        if random.random() <= self.reproduction_probability:
            self.children.append(
                Walker(
                    self.grid, 
                    self.grid_size, 
                    self.tortuous,
                    self.tortuousity_probability, 
                    self.reproduction_probability * WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER, # Child is twice as likely to die
                    min(self.death_probability * WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER, 1.0), # Child is twice as likely to die
                    (self.x, self.y),
                    rotate_vector(self.direction, self.get_random_small_angle())
                )
            )
    
    def make_move(self, turn_angle, movement_length):
        # Rotate the direction vector by TURN_ANGLE degrees
        self.direction = rotate_vector(self.direction, turn_angle)

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
            self.grid[math.floor(self.x)][math.floor(self.y)] = [255, 255, 255]
        
        self.points.append((self.x, self.y))
        self.turn_angles.append(turn_angle)
        self.check_bounds_and_die()

    def make_tortuous_move(self):
        final_turn_angle = self.get_random_small_angle() # After the tortuous turn, come back to this angle

        total_angle_turned = 0
        tortuous_points = [(self.x, self.y)]

        turn_angle = self.get_random_large_angle()
        self.make_move(
            turn_angle, 
            self.get_random_small_movement_length()
        )
        total_angle_turned += turn_angle
        tortuous_points.append((self.x, self.y))
        if self.dead:
            return
        
        turn_angle = self.get_random_large_angle()
        self.make_move(
            turn_angle, 
            self.get_random_small_movement_length()
        )
        total_angle_turned += turn_angle
        tortuous_points.append((self.x, self.y))
        if self.dead:
            return
        
        # Make a corrective turn to get back to the original angle
        self.make_move(
            final_turn_angle - total_angle_turned, 
            self.get_random_small_movement_length()
        )
        tortuous_points.append((self.x, self.y))
        if self.dead:
            return
        
        self.tortuous_points.append(tortuous_points)

    def get_tortuous_points(self):
        return self.tortuous_points + sum([child.get_tortuous_points() for child in self.children], [])

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