import numpy as np

def generate_centered_point(grid_size):
    # generate point thats not too in the center and not too close to the edges
    start = int(grid_size * 0.25)
    end = int(grid_size * 0.40)
    x = list(range(start, end)) + list(range(grid_size - end, grid_size - start))

    return (
        np.random.choice(x),
        np.random.choice(x)
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

def damped_sine(angle, amplitude, t):
    DAMPING_FACTOR = 0.1
    return amplitude * np.exp(-1 * DAMPING_FACTOR * t) * np.sin(np.radians(angle))

def normalize_vector(vector):
    norm = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return (vector[0] / norm, vector[1] / norm)

def add_vectors(vector_weight_pairs):
    x = 0
    y = 0
    remaining_weight = 1
    for vector, weight in vector_weight_pairs:
        if weight is not None:
            remaining_weight -= weight
        else:
            weight = remaining_weight
        x += vector[0] * weight
        y += vector[1] * weight
    return (x, y)