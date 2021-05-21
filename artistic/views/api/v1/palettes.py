from flask import Blueprint, Response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_sqlalchemy import sqlalchemy
import os

from artistic.models.palette import Palette
from artistic.views.api.v1.authenticate import authenticate_by_token

TOKEN = os.getenv('API_TOKEN')

palettes_bp = Blueprint('api.v1.palettes', __name__)

@palettes_bp.route('/api/v1/palettes/<id>/images', methods=['GET'])
@login_required
def show_by_images(id):
    palette = Palette.query.filter_by(image_id=id).first()
    if palette:
        return {'palette': palette.json()}
    else:
        return {}, 422

@palettes_bp.route('/api/v1/palettes', methods=['GET'])
@login_required
def index():
    palettes = [palette.json() for palette in current_user.palettes]
    return {'palettes': palettes}

@palettes_bp.route('/api/v1/palettes', methods=['POST'])
@login_required
def create():
    palette = Palette(
        hex_values=request.json['hex_values'],
        user_id=request.json['user_id'],
        image_id=request.json['image_id'],
        name=request.json['name'],
        )
    palette.save()
    return {'palette': palette.json()}


@palettes_bp.route('/api/v1/palettes/<id>', methods=['DELETE'])
@login_required
def delete(id):
    palette = Palette.query.get(id)
    palette.delete()

    return {}, 200
