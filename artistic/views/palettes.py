from flask import Blueprint, redirect, request, url_for
import os
from pathlib import Path
import artistic.kaggle as kaggle
import subprocess
from flask_login import current_user, login_required
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
            )
        if KAGGLE_ENABLED:
            kaggle.palette(
                image=palette,
                user_id=current_user.id,
                image_id=palette.id,
                palette_name=request.values['palette_name'],
                )
            subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
            Path(ROOT.joinpath('temp/palette.py')).unlink(missing_ok=True)
            Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)

    return redirect(url_for('home.main'))
