import cv2
import numpy as np
from pathlib import Path

from artistic.models import Image

ROOT = Path(__file__).parent
FILE_PATH = ROOT.joinpath('temp')

def black_and_white(starting_image, source_name):
    starting_path = FILE_PATH.joinpath(f'{starting_image.source_name}')
    starting_image.download(starting_path)

    originalImage = cv2.imread(str(starting_path))
    grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
  
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 100, 255, cv2.THRESH_BINARY)

    source_name = f'{source_name}.png'
    bnw_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(bnw_path), blackAndWhiteImage)
    image = Image.upload_artistic_photo(
        bnw_path,
        source_name,
        dims=(blackAndWhiteImage.shape[1], blackAndWhiteImage.shape[0]),
        )
    Path(starting_path).unlink()
    Path(bnw_path).unlink()

    return image

def black_and_white_outline(starting_image, outline_image, source_name):
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
            if (sum(copy[ridx][cidx]))/3 <= 127:
                copy[ridx][cidx] = [0,0,0]
            else:
                copy[ridx][cidx] = [255, 255, 255]

    for ridx, row in enumerate(img):
        for cidx, column in enumerate(row):
            if filled[ridx][cidx][0] == 255:
                copy[ridx][cidx] = img[ridx][cidx]


    source_name = f'{source_name}.png'
    bnw_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(bnw_path), copy)
    image = Image.upload_artistic_photo(
        bnw_path,
        source_name,
        dims=(copy.shape[1], copy.shape[0]),
        )
    Path(starting_path).unlink()
    Path(outline_path).unlink()
    Path(bnw_path).unlink()

    return image