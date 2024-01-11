import random
import numpy as np

def generate_centered_point(grid_size):
    return (
        random.randint(grid_size//10, grid_size - grid_size//10), 
        random.randint(grid_size//10, grid_size - grid_size//10)
    )

def bound(grid_size, x):
    if x < 0:
        return 0
    if x >= grid_size:
        return grid_size - 1
    return x

def rotate_vector(initial_direction, angle):
    initial_x, initial_y = initial_direction
    angle_rads = np.radians(angle)
    final_x = initial_x * np.cos(angle_rads) - initial_y * np.sin(angle_rads)
    final_y = initial_x * np.sin(angle_rads) + initial_y * np.cos(angle_rads)
    return (final_x, final_y)

def distance_2d(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)