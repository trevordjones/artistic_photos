from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_required
from flask_mail import Message
from flask_sqlalchemy import sqlalchemy
import os

from artistic.mail import mail
from artistic.models import Image, User
from artistic.views.api.v1.authenticate import authenticate_by_token

HTTP = os.getenv('HTTP_PROTOCOL')
BASE_URL = os.getenv('BASE_URL')

images_bp = Blueprint('api.v1.images', __name__)

@images_bp.route('/api/v1/images', methods=['GET'])
@login_required
def index():
    images = [image.json() for image in current_user.images if image.is_visible]
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

@images_bp.route('/api/v1/images/<id>/make_visible', methods=['PUT'])
@authenticate_by_token
def make_visible(id):
    image = Image.query.get(id)
    image.is_visible = True
    image.save()
    msg = Message('Photo Complete', recipients=[image.user.email])
    link = f'{HTTP}://{BASE_URL}?starting_id={image.id}'
    msg.html = f'''
        <h2>Your Artistic Photo is complete!</h2>
        <p><a href="{link}">Click here</a> to be taken to your photo</p>
        <p>Or <a href="{image.gcp_link()}">click here</a> to download your photo</p>
        '''
    mail.send(msg)
    return {'image': image.json()}

@images_bp.route('/api/v1/images', methods=['POST'])
@authenticate_by_token
def create():
    json_image = request.json['image']
    image = Image(
        user_id=json_image['user_id'],
        name=json_image['name'],
        source_name=json_image['source_name'],
        subdirectory='artistic',
        width=json_image['width'],
        height=json_image['height'],
        starting_image_id=json_image['starting_image_id'],
        )
    image.save()
    user = User.query.get(json_image['user_id'])
    msg = Message('Photo Complete', recipients=[user.email])
    link = f'{HTTP}://{BASE_URL}?starting_id={image.id}'
    msg.html = f'''
        <h2>Your Artistic Photo is complete!</h2>
        <p><a href="{link}">Click here</a> to be taken to your photo</p>
        <p>Or <a href="{image.gcp_link()}">click here</a> to download your photo</p>
        '''
    mail.send(msg)

    return {'image': image.json()}

@images_bp.route('/api/v1/images/<id>', methods=['DELETE'])
@login_required
def delete(id):
    image = Image.query.get(id)
    image.delete()

    return {}, 200
