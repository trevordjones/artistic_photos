from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_sqlalchemy import sqlalchemy

from artistic.models.image import Image

images_bp = Blueprint('api.v1.images', __name__)

@images_bp.route('/api/v1/images', methods=['GET'])
@login_required
def index():
    images = [image.json() for image in current_user.images]
    return {'images': images}

@images_bp.route('/api/v1/images/download/<id>', methods=['GET'])
@login_required
def download(id):
    image = current_user.images.filter(Image.id == int(id)).one()
    image.download()
    return {'image': image.json()}

@images_bp.route('/api/v1/images/<id>', methods=['GET'])
@login_required
def show(id):
    try:
        image = current_user.images.filter(Image.id == int(id)).one()
        return {'image': image.json()}
    except sqlalchemy.exc.NoResultFound:
        return {'image': {}}
