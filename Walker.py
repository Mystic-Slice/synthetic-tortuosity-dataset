import random
import math
import numpy as np

from config import ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND, LARGE_ANGLE_CUT_OFF, MOVEMENT_LENGTH_LIMITER, SINGLE_TURN_TURTUOUS, TURTUOUS_LENGTH_THRESHOLD
from util import bound, distance_2d, rotate_vector

class Walker:
    def __init__(self, grid, grid_size, turn_probability, initial_point = None):
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
        self.turn_probability = turn_probability

        # Choose a random direction vector
        norm = 0.0
        while norm == 0.0:
            dir_x = random.randint(-1, 1)
            dir_y = random.randint(-1, 1)
            norm = np.sqrt(dir_x ** 2 + dir_y ** 2)
        self.direction = (dir_x/norm , dir_y/norm)

        # Determine whether the walker has reached an edge
        self.dead = False
    
    def move(self):
        if self.dead:
            return False

        # Make a large turn based on the TURN_PROBABILITY
        large_turn = random.random() < self.turn_probability
        if large_turn:
            turn_angle = np.random.choice(
                list(range(ANGLE_LOWER_BOUND, ANGLE_UPPER_BOUND)) + 
                list(range(-ANGLE_UPPER_BOUND, -ANGLE_LOWER_BOUND))
            )
        else:
            turn_angle = np.random.choice(
                list(range(-ANGLE_LOWER_BOUND, ANGLE_LOWER_BOUND))
            )
        
        # Rotate the direction vector by TURN_ANGLE degrees
        self.direction = rotate_vector(self.direction, turn_angle)

        movement_length = random.randint(1, math.floor((self.grid_size - 1) * MOVEMENT_LENGTH_LIMITER))
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
        return True
        
    def find_tortuousity(self):
        turtuous_points = []
        for i in range(len(self.points) - 2):
            is_tortuous, points = self.is_tortuous(i)
            if(is_tortuous):
                if turtuous_points == []:
                    turtuous_points.append(set(points))
                else:
                    if self.points[i] in turtuous_points[-1]:
                        turtuous_points[-1].update(points)
                    else:
                        turtuous_points.append(set(points))
        return turtuous_points

    
    def is_tortuous(self, i):
        # Check in triples of points
        # See if the distance between the points is less than 5% of the grid size
        # See if large turns happened in both the points
        # If both the above conditions are satisfied, then the walker is tortuous
        p1 = self.points[i]
        p2 = self.points[i + 1]
        p3 = self.points[i + 2]

        turn_1_2 = self.turn_angles[i]
        turn_2_3 = self.turn_angles[i + 1]

        # If obtuse turns happen, it is turtuous
        if abs(turn_1_2) >= LARGE_ANGLE_CUT_OFF:
            return True & SINGLE_TURN_TURTUOUS, [p1]
        if abs(turn_2_3) >= LARGE_ANGLE_CUT_OFF:
            return True & SINGLE_TURN_TURTUOUS, [p2]

        if distance_2d(p1, p2) >= self.grid_size * TURTUOUS_LENGTH_THRESHOLD:
            return False, None

        if distance_2d(p2, p3) >= self.grid_size * TURTUOUS_LENGTH_THRESHOLD:
            return False, None
        
        if abs(turn_1_2) <= ANGLE_LOWER_BOUND:
            return False, None
        
        if abs(turn_2_3) <= ANGLE_LOWER_BOUND:
            return False, None
        
        return True, [p1, p2, p3]   