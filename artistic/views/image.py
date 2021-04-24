from PIL import Image as PILImage
import binascii
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from io import BytesIO
import os
from pathlib import Path
import subprocess

from artistic.kaggle_script import create_kaggle_script
from artistic.models.image import Image

ROOT = Path(__file__).parent.parent
KAGGLE_ENABLED = os.getenv('KAGGLE_ENABLED', default=False)


image_bp = Blueprint('images', __name__)
@image_bp.route('/images/starting', methods=['POST'])
@login_required
def starting():
    img = request.files['starting']
    if img.filename:
        image_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
        image = Image.upload_to_gcp(img, 'starting', image_name)
        img.seek(0)
        img_bytes = BytesIO(img.stream.read())
        img = PILImage.open(img_bytes)
        width, height = img.size
        image.user_id = current_user.id
        image.width = width
        image.height = height
        image.save()

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
        image_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
        image = Image.upload_to_gcp(img, 'style', image_name)
        img.seek(0)
        img_bytes = BytesIO(img.stream.read())
        img = PILImage.open(img_bytes)
        width, height = img.size
        image.user_id = current_user.id
        image.width = width
        image.height = height
        image.save()
        if KAGGLE_ENABLED:
            create_kaggle_script(starting_image.source_name, image.source_name, 'random')
            subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
            Path(ROOT.joinpath('temp/nst.py')).unlink(missing_ok=True)
            Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)

    return redirect(url_for('home.main'))
