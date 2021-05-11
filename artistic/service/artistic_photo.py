import binascii
from enum import Enum
import os

import artistic.kaggle as kaggle
import artistic.photo as photo

KAGGLE_ENABLED = bool(os.getenv('KAGGLE_ENABLED'))


class ArtisticActions(Enum):
    BLUR = 'blur'
    PENCIL_SKETCH = 'pencil_sketch'
    NST = 'nst'
    SHARPEN = 'sharpen'
    BLACK_AND_WHITE = 'black_and_white'
    

class ArtisticPhotoResponse:
    def __init__(self):
        self.error = None
        self.msg = None

    def is_valid(self):
        return not self.error


class ArtisticPhoto:
    def __init__(
            self,
            action,
            starting_image,
            outline_image=None,
            style_image=None):
        self.action = action
        self.starting_image = starting_image
        self.source_name = f'{binascii.b2a_hex(os.urandom(5)).decode("utf-8")}'
        self.outline_image = outline_image
        self.style_image = style_image

    def create(self):
        resp = ArtisticPhotoResponse()
        image = None
        if not self.starting_image:
            resp.error = 'Must include a starting image'
            return resp
        action = ArtisticActions(self.action)
        if action == ArtisticActions.PENCIL_SKETCH:
            image = photo.pencil_sketch(
                starting_image=self.starting_image,
                source_name=self.source_name,
                )
            resp.msg = 'Your sketch has been added'
        elif action == ArtisticActions.BLUR:
            if not self.outline_image:
                resp.error = 'Must draw an outline on a starting image'
            else:
                image = photo.blur(
                    starting_image=self.starting_image,
                    outline_image=self.outline_image,
                    source_name=self.source_name,
                    )
                resp.msg = 'Your blurred photo has been added'
        elif action == ArtisticActions.SHARPEN:
            image = photo.sharpen(
                starting_image=self.starting_image, 
                source_name=self.source_name)
            resp.msg = 'Your sharpened photo has been added'
        elif action == ArtisticActions.BLACK_AND_WHITE:
            if not self.outline_image:
                image = photo.black_and_white(
                    starting_image=self.starting_image,
                    source_name=self.source_name,
                )
                resp.msg = 'Your black and white photo has been added'
            else:
                image = photo.black_and_white_outline(
                    starting_image=self.starting_image,
                    outline_image=self.outline_image,
                    source_name=self.source_name,
                )
                resp.msg = 'Your black and white photo has been added'

        if KAGGLE_ENABLED:
            if action == ArtisticActions.NST:
                if not self.style_image:
                    resp.error = 'Must select a style image'
                else:
                    kaggle.nst(self.starting_image.source_name, self.style_image.source_name, 'random')
                    resp.msg = 'Adding style to your photo'
            if resp.is_valid():
                kaggle.run(f'{self.action}.py')
        return (resp, image)
