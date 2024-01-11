# Image configuration
GRID_SIZE = 1000

# Tortuosity configuration
TORTUOUSITY_PROBABILITY = 0.001
ANGLE_LOWER_BOUND = 15
ANGLE_UPPER_BOUND = 135

# Walker configuration
NUM_WALKERS = 20
MOVEMENT_LENGTH_LIMITER = 0.05 # percentage of grid size per step maximum allowed
TORTUOUS_MOVEMENT_LENGTH_LIMITER = 0.5 # applied over the MOVEMENT_LENGTH_LIMITER to get small jagged movements