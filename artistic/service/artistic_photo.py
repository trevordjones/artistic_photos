import binascii
from enum import Enum
import os

import artistic.kaggle as kaggle
from artistic.models import Image
import artistic.photo as photo

KAGGLE_ENABLED = bool(os.getenv('KAGGLE_ENABLED'))


class ArtisticActions(Enum):
    BLACK_AND_WHITE = 'black_and_white'
    BLUR = 'blur'
    PENCIL_SKETCH = 'pencil_sketch'
    NST = 'nst'
    SHARPEN = 'sharpen'
    TRANSFER_COLOR = 'transfer_color'


KAGGLE_ACTIONS = [ArtisticActions.NST, ArtisticActions.TRANSFER_COLOR]


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
            style_image=None,
            hex_value_map=None,
            palette=None,
            blur_range=16,
            nst_option=None,
            ):
        self.action = action
        self.starting_image = starting_image
        self.source_name = f'{binascii.b2a_hex(os.urandom(5)).decode("utf-8")}'
        self.outline_image = outline_image
        self.style_image = style_image
        self.blur_range = blur_range
        self.hex_value_map = hex_value_map
        self.palette = palette
        self.nst_option = nst_option

    def create(self):
        resp = ArtisticPhotoResponse()
        image = Image()
        if not self.starting_image:
            resp.error = 'Must include a starting image'
            return resp
        action = ArtisticActions(self.action)
        if action == ArtisticActions.PENCIL_SKETCH:
            if not self.outline_image:
                image = photo.pencil_sketch(
                    starting_image=self.starting_image,
                    source_name=self.source_name,
                )
            else:
                image = photo.pencil_sketch_outline(
                    starting_image=self.starting_image,
                    source_name=self.source_name,
                    outline_image=self.outline_image,
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
                    blur_range=self.blur_range,
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

        if KAGGLE_ENABLED and action in KAGGLE_ACTIONS:
            if action == ArtisticActions.NST:
                if not self.style_image:
                    resp.error = 'Must select a style image'
                else:
                    image = kaggle.nst(
                        self.starting_image,
                        self.style_image.source_name,
                        self.source_name,
                        self.nst_option,
                        )
                    resp.msg = 'Adding style to your photo'
            elif action == ArtisticActions.TRANSFER_COLOR:
                if not self.starting_image.palette:
                    resp.error = 'Please add a color palette to your starting image'
                else:
                    image = kaggle.transfer_color(
                        self.starting_image,
                        self.palette,
                        self.hex_value_map,
                        self.source_name,
                        )
                resp.msg = 'Watch out for an email for when your new photo is finished'
            if resp.is_valid():
                kaggle.run(f'{self.action}.py')
        return (resp, image)
