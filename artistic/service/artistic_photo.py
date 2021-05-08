from enum import Enum
import artistic.kaggle as kaggle
import os

KAGGLE_ENABLED = bool(os.getenv('KAGGLE_ENABLED'))


class ArtisticActions(Enum):
    BLUR = 'blur'
    NST = 'nst'

class ArtisticPhotoResponse:
    def __init__(self):
        self.error = None
        self.msg = None

    def is_valid(self):
        return not self.error


class ArtisticPhoto:
    def __init__(self, action, starting_image, outline_image=None, style_image=None):
        self.action = action
        self.starting_image = starting_image
        self.outline_image = outline_image
        self.style_image = style_image

    def create(self):
        resp = ArtisticPhotoResponse()
        if not self.starting_image:
            resp.error = 'Must include a starting image'
            return resp
        if KAGGLE_ENABLED:
            action = ArtisticActions(self.action)
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
