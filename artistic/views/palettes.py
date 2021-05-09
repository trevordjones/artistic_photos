from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required
import os
from pathlib import Path
import subprocess

import cv2
import artistic.photo as photo
from artistic.models import Image, Palette

ROOT = Path(__file__).parent.parent
PHOTO_PATH = ROOT.joinpath('photo/temp')

palettes_bp = Blueprint('palettes', __name__)

@palettes_bp.route('/images/palettes', methods=['POST'])
@login_required
def create():
    if request.form['palette_name']:
        if request.files['color_palette'].filename:
            file = request.files['color_palette']
            file_path = f'{PHOTO_PATH}/palette.png'
            file.save(file_path)
            hex_values = photo.palette(file_path, int(request.form['number']))

            palette = Palette(
                hex_values=hex_values,
                user_id=current_user.id,
                name=request.form['palette_name'],
                )
            palette.save()
            flash('Palette created', 'success')
            Path(file_path).unlink()
        else:
            flash('Please upload an image', 'danger')
    else:
        flash('Please name your palette', 'danger')

    return redirect(url_for('home.main'))
