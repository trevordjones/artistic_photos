from PIL import Image as PILImage
import binascii
from binascii import a2b_base64
import codecs
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from io import BytesIO
import os
import re
from werkzeug.datastructures import FileStorage

from artistic.models.image import Image
from artistic.service.artistic_photo import ArtisticPhoto

image_bp = Blueprint('images', __name__)
@image_bp.route('/images/starting', methods=['POST'])
@login_required
def starting():
    img = request.files['starting']
    if request.form['image_name']:
        if img.filename:
            image = Image.upload_to_gcp(img, 'starting')
            img.seek(0)
            img_bytes = BytesIO(img.stream.read())
            img = PILImage.open(img_bytes)
            width, height = img.size
            image.save(
                user_id=current_user.id,
                width=width,
                height=height,
                name=request.form['image_name'],
                )
            image.download()

            return redirect(url_for('home.main', starting=image.id))
        else:
            flash('Please upload an image', 'danger')
            return redirect(url_for('home.main'))
    else:
        flash('Please enter a name', 'danger')
        return redirect(url_for('home.main'))

@image_bp.route('/images/artistic', methods=['POST'])
@login_required
def artistic():
    if not request.values['starting_id']:
        flash('No starting image selected', 'danger')
        return redirect(url_for('home.main'))
    starting_image = Image.query.get(request.values['starting_id'])
    outline_image = None
    style_image = None
    if request.values['style_id']:
        style_image = Image.query.get(request.values['style_id'])
    if request.values['canvas_image']:
        pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        img_bytes = pattern.match(request.values['canvas_image']).group(2)
        binary_data = a2b_base64(img_bytes)
        img = FileStorage(BytesIO(binary_data), 'outline.png')
        outline_image = Image.upload_to_gcp(img, 'starting')
        img = PILImage.open(BytesIO(binary_data))
        width, height = img.size
        outline_image.save(
            user_id=current_user.id,
            width=width,
            height=height,
            starting_image_id=starting_image.id,
            )

    resp, artistic_image = ArtisticPhoto(
        request.form['action'],
        starting_image,
        outline_image=outline_image,
        style_image=style_image,
        ).create()
    artistic_image.save(user_id=current_user.id, name=request.form['artistic_name'])

    if resp.is_valid():
        flash(resp.msg, 'success')
    else:
        flash(resp.error, 'danger')
    return redirect(url_for('home.main'))

@image_bp.route('/images/style', methods=['POST'])
@login_required
def style():
    if request.files['style'].filename:
        img = request.files['style']
        style_image = Image.upload_to_gcp(img, 'style')
        img.seek(0)
        img_bytes = BytesIO(img.stream.read())
        img = PILImage.open(img_bytes)
        width, height = img.size
        style_image.save(
            user_id=current_user.id,
            width=width,
            height=height,
        )

    flash('Style image uploaded', 'success')
    return redirect(url_for('home.main'))
