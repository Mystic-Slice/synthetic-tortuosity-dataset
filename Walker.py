import random
import math
import numpy as np

from config import ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND, MOVEMENT_LENGTH_LIMITER, TORTUOUS_MOVEMENT_LENGTH_LIMITER
from util import bound, rotate_vector

class Walker:
    def __init__(self, grid, grid_size, tortuousity_probability, initial_point = None):
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

        # Choose a random direction vector
        norm = 0.0
        while norm == 0.0:
            dir_x = random.randint(-1, 1)
            dir_y = random.randint(-1, 1)
            norm = np.sqrt(dir_x ** 2 + dir_y ** 2)
        self.direction = (dir_x/norm , dir_y/norm)

        # Determine whether the walker has reached an edge
        self.dead = False

        self.tortuous = False
        self.tortuous_points = []
    
    def move(self):
        if self.dead:
            return False

        # Make a large turn based on the TURN_PROBABILITY
        tortuous_turn = random.random() < self.tortuousity_probability

        if tortuous_turn and not self.tortuous: # Only one tortuous turn per walker max
            tortuous_points = [(self.x, self.y)]
            self.make_move(
                self.get_random_large_angle(),
                self.get_random_small_movement_length()
            )
            tortuous_points.append((self.x, self.y))

            if self.dead:
                return True
            
            self.make_move(
                self.get_random_large_angle(),
                self.get_random_small_movement_length()
            )
            tortuous_points.append((self.x, self.y))

            if self.dead:
                return True
            
            self.make_move(
                self.get_random_large_angle(),
                self.get_random_small_movement_length()
            )
            tortuous_points.append((self.x, self.y))

            self.tortuous = True
            self.tortuous_points += tortuous_points
        else:
            self.make_move(
                self.get_random_small_angle(),
                self.get_random_movement_length()
            )
        return True
    
    def make_move(self, turn_angle, movement_length):
        # Rotate the direction vector by TURN_ANGLE degrees
        self.direction = rotate_vector(self.direction, turn_angle)

        final_pos_x = bound(self.grid_size, self.x + self.direction[0] * movement_length)
        final_pos_y = bound(self.grid_size, self.y + self.direction[1] * movement_length)

        # If the walker has reached an edge, it dies
        if final_pos_x == self.grid_size - 1 or \
            final_pos_y == self.grid_size - 1 or \
            final_pos_x == 0 or \
            final_pos_y == 0:
            self.dead = True

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