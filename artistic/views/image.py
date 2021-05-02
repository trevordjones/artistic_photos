from PIL import Image as PILImage
import binascii
from binascii import a2b_base64
import codecs
from flask import Blueprint, redirect, render_template, request, url_for
import re
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from io import BytesIO
import os
from pathlib import Path
import subprocess

import artistic.kaggle as kaggle
from artistic.models.image import Image

ROOT = Path(__file__).parent.parent
KAGGLE_ENABLED = os.getenv('KAGGLE_ENABLED', default=False)


image_bp = Blueprint('images', __name__)
@image_bp.route('/images/starting', methods=['POST'])
@login_required
def starting():
    img = request.files['starting']
    if img.filename:
        image = Image.upload_to_gcp(img, 'starting')
        img.seek(0)
        img_bytes = BytesIO(img.stream.read())
        img = PILImage.open(img_bytes)
        width, height = img.size
        image.user_id = current_user.id
        image.width = width
        image.height = height
        image.save()
        image.download()

        return redirect(url_for('home.main', starting=image.id))
    else:
        return redirect(url_for('home.main'))

@image_bp.route('/images/artistic', methods=['POST'])
@login_required
def artistic():
    if not request.values['starting_id']:
        # todo - send an error message
        return redirect(url_for('home.main'))
    starting_image = Image.query.get(request.values['starting_id'])
    if request.files['style'].filename:
        img = request.files['style']
        image = Image.upload_to_gcp(img, 'style')
        img.seek(0)
        img_bytes = BytesIO(img.stream.read())
        img = PILImage.open(img_bytes)
        width, height = img.size
        image.user_id = current_user.id
        image.width = width
        image.height = height
        image.starting_image_id = rqeuest.values['starting_id']
        image.save()
        if KAGGLE_ENABLED:
            kaggle.nst(starting_image.source_name, image.source_name, 'random')
            subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
            Path(ROOT.joinpath('temp/nst.py')).unlink(missing_ok=True)
            Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)
    if request.values['canvas_image']:
        pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        img_bytes = pattern.match(request.values['canvas_image']).group(2)
        binary_data = a2b_base64(img_bytes)
        img = FileStorage(BytesIO(binary_data), 'outline.png')
        image = Image.upload_to_gcp(img, 'starting')
        img = PILImage.open(BytesIO(binary_data))
        width, height = img.size
        image.user_id = current_user.id
        image.width = width
        image.height = height
        image.starting_image_id = request.values['starting_id']
        image.save()
    if request.values['blur']:
        starting_image = Image.query.get(request.values['starting_id'])
        if KAGGLE_ENABLED:
            kaggle.blur(outline_image=image, starting_image=starting_image)
            subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
            Path(ROOT.joinpath('temp/blur.py')).unlink(missing_ok=True)
            Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)

    return redirect(url_for('home.main'))
