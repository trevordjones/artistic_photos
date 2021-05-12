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
    def create_palette(photo_path):
        num_palettes = int(request.form['number']) if request.form['number'] else 6
        hex_values = photo.palette(photo_path, num_palettes=num_palettes)

        palette = Palette(
            hex_values=hex_values,
            user_id=current_user.id,
            name=request.form['palette_name'],
            )
        Path(photo_path).unlink()
        flash('Palette created', 'success')
        return palette

    if request.form['palette_name']:
        if 'use_starting_image' in request.form:
            if request.form['starting_image_id']:
                image = Image.query.get(request.form['starting_image_id'])
                image.download(f'{PHOTO_PATH}/{image.source_name}')
                palette = create_palette(f'{PHOTO_PATH}/{image.source_name}')
                palette.image_id = image.id
                palette.save()
            else:
                flash('Please select an image to start with', 'danger')
        elif request.files['color_palette'].filename:
            file = request.files['color_palette']
            file_path = f'{PHOTO_PATH}/palette.png'
            file.save(file_path)
            palette = create_palette(file_path)
            palette.save()
        else:
            flash('Please upload an image or select an image to start with', 'danger')
    else:
        flash('Please name your palette', 'danger')

    return redirect(url_for('home.main'))
