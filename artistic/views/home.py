import binascii
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
import os
from pathlib import Path

from artistic.models.image import Image

ROOT = Path(__file__).parent.parent
KAGGLE_ENABLED - os.getenv('KAGGLE_ENABLED', default=False)

home_bp = Blueprint('home', __name__)
@home_bp.route('/', methods=['GET', 'POST'])
@login_required
def main():
    import subprocess

    from artistic.kaggle_script import create_kaggle_script

    if request.method == 'GET':
        return render_template('home/index.html')
    else:
        content_image = Image()
        image_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
        names = {'content': '', 'style': ''}
        try:
            for key in request.files:
                image = Image.upload_to_gcp(request.files[key], key, image_name)
                image.user_id = current_user.id
                names[key] = image.source_name
                image.save()
                if key == 'content':
                    content_image = image

            if KAGGLE_ENABLED:
                create_kaggle_script(names['content'], names['style'], 'random')
                subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
                Path(ROOT.joinpath('temp/nst.py')).unlink(missing_ok=True)
                Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)
        except Exception as e:
            print(e)

        return redirect(url_for('home.main', starting=content_image.id))
