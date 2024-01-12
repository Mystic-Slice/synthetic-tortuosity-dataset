# Image configuration
GRID_SIZE = 1000

# Tortuosity configuration
TORTUOUSITY_PROBABILITY = 0.01
TORTUOUSITY_AFTER_STEPS = 5 # Tortuousity is only allowed after this many steps, otherwise gets hidden in the dense central region
ANGLE_LOWER_BOUND = 15
ANGLE_UPPER_BOUND = 135
TORTUOUS_MOVEMENT_LENGTH_LIMITER = 0.3 # applied over the MOVEMENT_LENGTH_LIMITER to get small jagged movements

# Walker configuration
NUM_WALKERS = 20
WALKER_MATURITY_STEPS = 5
WALKER_INITIAL_REPRODUCTION_PROBABILITY = 0.4
WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER = 0.1
WALKER_INITIAL_DEATH_PROBABILITY = 0.05
WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER = 2
MOVEMENT_LENGTH_LIMITER = 0.05 # percentage of grid size per step maximum allowed