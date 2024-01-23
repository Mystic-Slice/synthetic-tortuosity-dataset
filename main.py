from PIL import Image
import numpy as np
import pandas as pd
import os
import datetime
import tqdm

from Walker import Walker
from util import generate_centered_point, rotate_vector
from config import GRID_SIZE, NUM_WALKERS, WALKER_INITIAL_DEATH_PROBABILITY, WALKER_INITIAL_REPRODUCTION_PROBABILITY

def generate_image(tortuous_image):

    img = [[[0, 0, 0] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Spawn walkers somewhere in the middle of the image
    INITIAL_POINT = generate_centered_point(GRID_SIZE)

    walkers = [
            Walker(
                img, 
                GRID_SIZE, 
                tortuous_image,
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
            break

    # Write the image to a file
    img = np.array(img, dtype=np.uint8)
    img = Image.fromarray(img)

    return img

DEBUG = 0
if DEBUG:
    img = generate_image(True)
    img.save("tortuous.png")

    img = generate_image(False)
    img.save("non_tortuous.png")
else:
    os.makedirs("images/tortuous", exist_ok=True)
    os.makedirs("images/non_tortuous", exist_ok=True)

    start = datetime.datetime.now()
    NUM_IMAGES_PER_CLASS = 100
    num_images = 0
    files = {}

    print("Generating Tortuous Images")
    for i in tqdm.tqdm(range(NUM_IMAGES_PER_CLASS)):
        img = generate_image(True)
        filename = f"images/tortuous/{i}.png"
        files[num_images] = {"filename": filename, "tortuous": 1}
        img.save(filename)
        num_images += 1

    print("Generating Non-Tortuous Images")
    for i in tqdm.tqdm(range(NUM_IMAGES_PER_CLASS)):
        img = generate_image(False)
        filename = f"images/non_tortuous/{i}.png"
        files[num_images] = {"filename": filename, "tortuous": 0}
        img.save(filename)
        num_images += 1

    df = pd.DataFrame.from_dict(files, orient="index")
    df.to_csv("images/data.csv", index=False)

    end = datetime.datetime.now()
    print(f"Time taken = {end-start} to generate {NUM_IMAGES_PER_CLASS * 2} images")