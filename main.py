from PIL import Image
import numpy as np
import pandas as pd
import os
import datetime
import tqdm
import shutil
import math 
from Walker import Walker
from util import bound, generate_centered_point, rotate_vector
from config import GRID_SIZE, NUM_TORTUOUS_WALKERS, NUM_WALKERS, WALKER_INITIAL_REPRODUCTION_PROBABILITY

def generate_image(tortuous_image):
    img = [[[0, 0, 0] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Spawn walkers somewhere in the middle of the image
    SOURCE_POINT = generate_centered_point(GRID_SIZE)
    
    # Initialize walkers
    walkers = []
    if tortuous_image:
        walker_is_tortuous = [False] * (NUM_WALKERS - NUM_TORTUOUS_WALKERS) + [True] * NUM_TORTUOUS_WALKERS
        np.random.shuffle(walker_is_tortuous)
    else:
        walker_is_tortuous = [False] * NUM_WALKERS
    for i in range(NUM_WALKERS):
        # Slightly move the walker away from the initial point in all directions uniformly
        # This is because, the vector field force direction is undefined at the source
        initial_x, initial_y = SOURCE_POINT
        angle = (360 / NUM_WALKERS) * i
        start_x = bound(
            GRID_SIZE,
            initial_x + np.cos(angle) * GRID_SIZE * 0.01
        )
        start_y = bound(
            GRID_SIZE,
            initial_y + np.sin(angle) * GRID_SIZE * 0.01
        )
        start_point = (start_x, start_y)

        walker = Walker(
                grid = img, 
                grid_size = GRID_SIZE,
                tortuous = walker_is_tortuous[i],
                reproduction_probability = WALKER_INITIAL_REPRODUCTION_PROBABILITY,
                initial_point = start_point,
                source_point = SOURCE_POINT,
                initial_direction = rotate_vector((1, 0), (i * 360) / NUM_WALKERS) # Spread the walkers out evenly
            )
        walkers.append(walker)

    # Let the walkers move until they all die
    while True:
        alive = False
        for walker in walkers:
            alive |= walker.move()

        if not alive:
            break

    # Get the tortuous points
    tortuous_points = []
    for w in walkers:
        if w.tortuous:
            tortuous_points += w.get_tortuous_points()

    tortuous_points = sum([list(point_set) for point_set in tortuous_points], [])
    tortuous_points = list(set(tortuous_points))

    # # Calculate the bounding box for the tortuous regions
    # bounding_box_coords = []
    # for points_set in tortuous_points:
    #     max_x = max([p[0] for p in points_set])
    #     max_x = bound(GRID_SIZE, math.floor(max_x + GRID_SIZE * 0.01))
    #     min_x = min([p[0] for p in points_set])
    #     min_x = bound(GRID_SIZE, math.floor(min_x - GRID_SIZE * 0.01))

    #     max_y = max([p[1] for p in points_set])
    #     max_y = bound(GRID_SIZE, math.floor(max_y + GRID_SIZE * 0.01))
    #     min_y = min([p[1] for p in points_set])
    #     min_y = bound(GRID_SIZE, math.floor(min_y - GRID_SIZE * 0.01))

    #     # Uncomment to draw the bounding box
    #     for x in range(min_x, max_x + 1):
    #         img[x][min_y] = [255, 0, 0]
    #         img[x][max_y] = [255, 0, 0]
        
    #     for y in range(min_y, max_y + 1):
    #         img[min_x][y] = [255, 0, 0]
    #         img[max_x][y] = [255, 0, 0]
    #     bounding_box_coords.append([(min_x, min_y), (max_x, max_y)])

    # Write the image to a file
    img = np.array(img, dtype=np.uint8)

    # Crop out the edges
    start_index = int(GRID_SIZE * 0.2)
    end_index = int(GRID_SIZE * 0.8)
    img = img[start_index:end_index, start_index:end_index]

    # Remove the corresponding tortuous points and fix the coordinates to adjust for the cropping
    tortuous_points = [
        (x-start_index, y-start_index) for x, y in tortuous_points 
        if start_index <= x < end_index and start_index <= y < end_index
    ]


    img = Image.fromarray(img)

    return img, tortuous_points

DEBUG = 0
if DEBUG:
    img, _ = generate_image(True)
    img.save("tortuous.png")

    img, _ = generate_image(False)
    img.save("non_tortuous.png")
else:
    shutil.rmtree("images", ignore_errors=True)
    os.makedirs("images/tortuous", exist_ok=True)
    os.makedirs("images/non_tortuous", exist_ok=True)

    start = datetime.datetime.now()
    NUM_IMAGES_PER_CLASS = 1000
    num_images = 0
    files = {}

    print("Generating Tortuous Images")
    for i in tqdm.tqdm(range(NUM_IMAGES_PER_CLASS)):
        img, tortuous_points = generate_image(True)
        filename = f"images/tortuous/{i}.png"
        files[num_images] = {
            "filename": filename, 
            "tortuous": 1,
            "tortuous_points": tortuous_points
        }
        img.save(filename)
        num_images += 1

    print("Generating Non-Tortuous Images")
    for i in tqdm.tqdm(range(NUM_IMAGES_PER_CLASS)):
        img, tortuous_points = generate_image(False)
        filename = f"images/non_tortuous/{i}.png"
        files[num_images] = {
            "filename": filename,
            "tortuous": 0,
            "tortuous_points": tortuous_points
        }
        img.save(filename)
        num_images += 1

    df = pd.DataFrame.from_dict(files, orient="index")
    df.to_csv("images/data.csv", index=False, sep="\t")

    end = datetime.datetime.now()
    print(f"Time taken = {end-start} to generate {NUM_IMAGES_PER_CLASS * 2} images")