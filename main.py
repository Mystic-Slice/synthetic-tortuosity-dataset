from PIL import Image
import numpy as np
import math
import pandas as pd
import random
import os
import time
import tqdm

from Walker import Walker
from util import generate_centered_point, bound, rotate_vector
from config import GRID_SIZE, NUM_WALKERS, TORTUOUS_WALKERS, TORTUOUSITY_PROBABILITY, WALKER_INITIAL_DEATH_PROBABILITY, WALKER_INITIAL_REPRODUCTION_PROBABILITY

def generate_image(draw_bounding_box=False):

    tortuous_image = random.random() < 0.5 # 50% chance of generating a tortuous image

    img = [[[0, 0, 0] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Spawn walkers somewhere in the middle of the image
    INITIAL_POINT = generate_centered_point(GRID_SIZE)

    walkers = [
            Walker(
                img, 
                GRID_SIZE, 
                (random.random() <= TORTUOUS_WALKERS) and tortuous_image, # if tortuous image, 50% of all walkers follow tortuous path
                TORTUOUSITY_PROBABILITY, 
                WALKER_INITIAL_REPRODUCTION_PROBABILITY,
                WALKER_INITIAL_DEATH_PROBABILITY,
                INITIAL_POINT,
                rotate_vector((1, 0), (i * 360) / NUM_WALKERS) # Spread the walkers out evenly
            ) 
            for i in range(NUM_WALKERS)
        ]

    while True:
        alive = False
        for walker in walkers:
            alive |= walker.move()

        if not alive:
            # print("All walkers dead")
            break

    tortuous_points = []
    tortuous = False
    for w in walkers:
        tortuous |= w.tortuous
        if w.tortuous:
            tortuous_points += w.get_tortuous_points()

    if draw_bounding_box:
        # Mark the tortuous points red
        for points_set in tortuous_points:
            max_x = max([p[0] for p in points_set])
            max_x = bound(GRID_SIZE, math.floor(max_x + GRID_SIZE * 0.01))
            min_x = min([p[0] for p in points_set])
            min_x = bound(GRID_SIZE, math.floor(min_x - GRID_SIZE * 0.01))

            max_y = max([p[1] for p in points_set])
            max_y = bound(GRID_SIZE, math.floor(max_y + GRID_SIZE * 0.01))
            min_y = min([p[1] for p in points_set])
            min_y = bound(GRID_SIZE, math.floor(min_y - GRID_SIZE * 0.01))

            for x in range(min_x, max_x + 1):
                img[x][min_y] = [255, 0, 0]
                img[x][max_y] = [255, 0, 0]
            
            for y in range(min_y, max_y + 1):
                img[min_x][y] = [255, 0, 0]
                img[max_x][y] = [255, 0, 0]

    # Write the image to a file
    img = np.array(img, dtype=np.uint8)
    img = Image.fromarray(img)

    return img, tortuous

os.makedirs("images/tortuous", exist_ok=True)
os.makedirs("images/non_tortuous", exist_ok=True)

start = time.time()
NUM_IMAGES_PER_CLASS = 100
num_images = 0
num_tortuous = 0
num_non_tortuous = 0
files = {}

tqdm_meter = tqdm.tqdm(total=NUM_IMAGES_PER_CLASS * 2)
while num_images < NUM_IMAGES_PER_CLASS * 2:
    img, is_tortuous = generate_image()
    if is_tortuous:
        if num_tortuous >= NUM_IMAGES_PER_CLASS:
            continue
        filename = f"images/tortuous/{num_tortuous}.png"
        files[num_images] = {"filename": filename, "tortuous": 1}
        img.save(filename)
        num_tortuous += 1
        num_images += 1
        tqdm_meter.update(1)
    else:
        if num_non_tortuous >= NUM_IMAGES_PER_CLASS:
            continue
        filename = f"images/non_tortuous/{num_non_tortuous}.png"
        files[num_images] = {"filename": filename, "tortuous": 0}
        img.save(filename)
        num_non_tortuous += 1
        num_images += 1
        tqdm_meter.update(1)
tqdm_meter.close()

df = pd.DataFrame.from_dict(files, orient="index")
df.to_csv("images/data.csv", index=False)

end = time.time()
print(f"Time taken: {end - start} seconds to generate {NUM_IMAGES_PER_CLASS * 2} images")