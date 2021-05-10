import cv2
import numpy as np
from pathlib import Path

from artistic.models import Image

ROOT = Path(__file__).parent
FILE_PATH = ROOT.joinpath('temp')

def sharpen(starting_image, source_name):
    starting_path = FILE_PATH.joinpath(f'{starting_image.source_name}')
    starting_image.download(starting_path)
    starting_image = cv2.imread(str(starting_path))

    sharpening_filter = np.array([[-1, -1, -1],
                                    [-1, 9, -1],
                                    [-1, -1, -1]])

    sharpened_image = cv2.filter2D(starting_image, -1, sharpening_filter)
    
    source_name = f'{source_name}.png'
    sharpen_path = FILE_PATH.joinpath(f'{source_name}')
    cv2.imwrite(str(sharpen_path), sharpened_image)
    image = Image.upload_artistic_photo(
        sharpen_path,
        source_name,
        dims=(sharpened_image.shape[1], sharpened_image.shape[0]),
        )
    Path(starting_path).unlink()
    Path(sharpen_path).unlink()

    return image
    