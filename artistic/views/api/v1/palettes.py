import os
from flask import Blueprint, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required
from flask_sqlalchemy import sqlalchemy

from artistic.models.palette import Palette
TOKEN = os.getenv('PALETTE_TOKEN')

palettes_bp = Blueprint('api.v1.palettes', __name__)

@palettes_bp.route('/api/v1/palettes', methods=['GET'])
def index():
    palettes = [palette.json() for palette in current_user.palettes]
    return {'palettes': palettes}

@palettes_bp.route('/api/v1/palettes', methods=['POST'])
def create():
    token = request.headers['Token']
    if token == TOKEN:
        palette = Palette(
            hex_values=request.json['hex_values'],
            user_id=request.json['user_id'],
            image_id=request.json['image_id'],
            name=request.json['name'],
            )
        palette.save()
        return {'palette': palette.json()}
    else:
        return {'unauthorized': 'Token invalid'}, 401

