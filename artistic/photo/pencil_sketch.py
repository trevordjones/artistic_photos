import binascii
import cv2
import numpy as np
import os
from pathlib import Path

from artistic.models import Image

ROOT = Path(__file__).parent
FILE_PATH = ROOT.joinpath('temp')


def pencil_sketch(starting_image, source_name):
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
    source_name = f'{source_name}.png'
    sketch_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(sketch_path), sketch)
    image = Image.upload_artistic_photo(
        sketch_path,
        source_name,
        dims=(sketch.shape[1], sketch.shape[0]),
        )
    Path(starting_path).unlink()
    Path(sketch_path).unlink()

    return image

def pencil_sketch_outline(starting_image, source_name, outline_image):
    starting_path = FILE_PATH.joinpath(f'{starting_image.source_name}')
    outline_path = FILE_PATH.joinpath(f'{outline_image.source_name}')
    starting_image.download(starting_path)
    outline_image.download(outline_path)

    img = cv2.imread(str(starting_path))
    outline = cv2.imread(str(outline_path))
    outline = cv2.cvtColor(outline, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (outline.shape[1], outline.shape[0]))

    lower = np.array([255, 0, 0], dtype = "uint8")
    upper = np.array([255, 0, 0], dtype = "uint8")
    mask = cv2.inRange(outline, lower, upper)
    traced = cv2.bitwise_and(outline, outline, mask = mask)
    grayed = cv2.cvtColor(traced, cv2.COLOR_RGB2GRAY)

    filled = grayed.copy()
    contours,_ = cv2.findContours(filled, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image_binary = np.zeros((filled.shape[0], filled.shape[1], 1), dtype=np.uint8)
    filled = cv2.drawContours(image_binary, [max(contours, key = cv2.contourArea)], -1, 255, thickness=-1)

    copy = img.copy()

    for ridx, row in enumerate(copy):
        for cidx, column in enumerate(row):
            mid = (0.2989*copy[ridx][cidx][0]) + (0.5870*copy[ridx][cidx][1]) + (0.1140*copy[ridx][cidx][2]) 
            copy[ridx][cidx] = [mid, mid, mid]

    invert = cv2.bitwise_not(copy)
    smoothing = cv2.GaussianBlur(invert, (11, 11), sigmaX=0, sigmaY=0)
    divide = cv2.divide(copy, 255 - smoothing, scale=256)

    sketch = divide.copy()
    sketch = sketch - ((255 - sketch) * 10)

    for ridx, row in enumerate(img):
        for cidx, column in enumerate(row):
            if filled[ridx][cidx][0] == 255:
                sketch[ridx][cidx] = img[ridx][cidx]

    source_name = f'{source_name}.png'
    sketch_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(sketch_path), sketch)
    image = Image.upload_artistic_photo(
        sketch_path,
        source_name,
        dims=(sketch.shape[1], sketch.shape[0]),
        )
    Path(starting_path).unlink()
    Path(outline_path).unlink()
    Path(sketch_path).unlink()

    return image
