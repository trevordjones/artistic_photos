from enum import Enum
import artistic.kaggle as kaggle
import artistic.photo as photo
import os
import binascii

KAGGLE_ENABLED = bool(os.getenv('KAGGLE_ENABLED'))


class ArtisticActions(Enum):
    BLUR = 'blur'
    PENCIL_SKETCH = 'pencil_sketch'
    NST = 'nst'

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
            artistic_name=None,
            outline_image=None,
            style_image=None):
        self.action = action
        self.starting_image = starting_image
        if not artistic_name:
            self.artistic_name = f'{binascii.b2a_hex(os.urandom(5)).decode("utf-8")}'
        else:
            self.artistic_name = artistic_name
        self.outline_image = outline_image
        self.style_image = style_image

    def create(self):
        resp = ArtisticPhotoResponse()
        if not self.starting_image:
            resp.error = 'Must include a starting image'
            return resp
        action = ArtisticActions(self.action)
        if action == ArtisticActions.PENCIL_SKETCH:
            photo.pencil_sketch(starting_image=self.starting_image, name=self.artistic_name)
            resp.msg = 'Your sketch has been added'

        if KAGGLE_ENABLED:
            if action == ArtisticActions.BLUR:
                if not self.outline_image:
                    resp.error = 'Must draw a border on a starting image'
                else:
                    kaggle.blur(outline_image=self.outline_image, starting_image=self.starting_image)
                    resp.msg = 'Blurring your photo'
            elif action == ArtisticActions.NST:
                if not self.style_image:
                    resp.error = 'Must select a style image'
                else:
                    kaggle.nst(self.starting_image.source_name, self.style_image.source_name, 'random')
                    resp.msg = 'Adding style to your photo'
            if resp.is_valid():
                kaggle.run(f'{self.action}.py')
        return resp
