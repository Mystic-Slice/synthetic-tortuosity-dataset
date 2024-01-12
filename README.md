# Dataset Generator - mimics Tortuousity in Retinal Blood Vessels

`Walker`s randomly choose and follow a path from the start point. They die when they hit the edge of the grid or sometimes randomly (based on a death probability). Each `Walker` can reproduce to create a child to produce the branching effect.

A `Walker` is set to be either tortuous or non-tortuous when created. If tortuous, they make a tortuous movement randomly (based on a tortuousity probability). The children inherity the tortuousity of their parent.

By default, in a tortuous image, half of the `Walker`s are set to be tortuous. This can be changed in the `config.py` file.

The grid size (image size), the number of `Walker`s, the tortuousity probability and a few other parameters can be set in the `config.py` file.

## Sample Generated Images:

### Tortuous:
#### Tortuous Retinal Blood Vessels:
![Tortuous Eye](sample/tortuous_eye.png)
#### Tortuous Sample Generated:
![Tortuous](sample/tortuous.png)

### Non-Tortuous:
#### Non-Tortuous Retinal Blood Vessels:
![Non-Tortuous Eye](sample/non_tortuous_eye.png)
#### Non-Tortuous Sample Generated:
![Non-Tortuous](sample/non_tortuous.png)

## Config Parameters:
1. `GRID_SIZE`: Size of the grid (image) in pixels.
2. `TORTUOUSITY_PROBABILITY`: Probability of a `Walker` making a tortuous movement. (recommended: 0.1)
3. `ANGLE_LOWER_BOUND`: Lower bound of the angle of the tortuous movement. (recommended: 15)
4. `ANGLE_UPPER_BOUND`: Upper bound of the angle of the tortuous movement. (recommended: 90)
5. `MOVEMENT_LENGTH_LIMITER`: Limit the length of a single step of a `Walker`. As a percentage of the total grid size. (recommended: 0.05)
6. `TORTUOUS_MOVEMENT_LENGTH_LIMITER`: Limit the length of a single step of a `Walker` when it is making a tortuous movement. Applied over `MOVEMENT_LENGTH_LIMIER`. (recommended: 0.3)
7. `NUM_WALKERS`: Number of `Walker`s to be generated.
8. `WALKER_MATURITY_STEPS`: Number of steps a `Walker` has to take before it can reproduce. To prevent too many branches in the center.
9. `TURTUOUS_WALKERS`: Ratio of `Walker`s to be set as tortuous in a tortuous image. (recommended: 0.7)
10. `WALKER_INITIAL_REPRODUCTION_PROBABILITY`: Probability of a `Walker` reproducing when it is mature. (recommended: 0.3)
11. `WALKER_CHILD_REPRODUCTION_PROBABILITY_MULTIPLIER`: Multiplier for the reproduction probability of a `Walker`'s child. Should be decreasing to avoid population boom. (recommended: 0.1 (child 10 times less likely to reproduce))
12. `WALKER_INITIAL_DEATH_PROBABILITY`: Probability of a `Walker` dying when it is mature. (recommended: 0.05)
13. `WALKER_CHILD_DEATH_PROBABILITY_MULTIPLIER`: Multiplier for the death probability of a `Walker`'s child. Should be increasing to avoid population boom. (recommended: 2 (child twice as likely to die))

## How to use:
Code in `main.py` helps generate a dataset of images. The images are stored in a folder along with a csv file with filenames and tortuousity labels.


### To generate sample image:
```py
img, is_tortuous = generate_image(draw_bounding_box=True)
img.save("sample.png")
print(f"Tortuosity: {is_tortuous}")
```