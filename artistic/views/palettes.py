from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_required
import os
from pathlib import Path
import subprocess

import artistic.kaggle as kaggle
from artistic.models.image import Image

ROOT = Path(__file__).parent.parent
KAGGLE_ENABLED = os.getenv('KAGGLE_ENABLED', default=False)

palettes_bp = Blueprint('palettes', __name__)

@palettes_bp.route('/images/palettes', methods=['POST'])
@login_required
def create():
    if request.files['color_palette'].filename:
        file = request.files['color_palette']
        palette = Image.upload_to_gcp(file, 'palette')
        palette.save(
            file=file,
            user_id=current_user.id,
            name=request.values['palette_name'],
            )
        if KAGGLE_ENABLED:
            kaggle.palette(
                image=palette,
                user_id=current_user.id,
                image_id=palette.id,
                palette_name=request.values['palette_name'],
                )
            kaggle.run('palette.py')

    return redirect(url_for('home.main'))
