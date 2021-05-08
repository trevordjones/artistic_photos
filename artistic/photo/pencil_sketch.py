import binascii
import cv2
import numpy as np
import os
from pathlib import Path

from artistic.models import Image

ROOT = Path(__file__).parent
FILE_PATH = ROOT.joinpath('temp')


def pencil_sketch(starting_image, name):
    starting_path = FILE_PATH.joinpath(f'{starting_image.source_name}')
    starting_image.download(starting_path)
    img = cv2.imread(str(starting_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    invert = cv2.bitwise_not(gray)
    smoothing = cv2.GaussianBlur(invert, (21, 21), sigmaX=0, sigmaY=0)
    divide = cv2.divide(gray, 255 - smoothing, scale=256)

    sketch = divide.copy()
    sketch = sketch - ((255 - sketch) * 10)
    source_name = f'{name}.png'
    sketch_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(sketch_path), sketch)
    image = Image.upload_artistic_photo(
        sketch_path,
        source_name,
        dims=(sketch.shape[0], sketch.shape[1]),
        )
    image.name = name
    Path(starting_path).unlink()
    Path(sketch_path).unlink()
    image.save()
