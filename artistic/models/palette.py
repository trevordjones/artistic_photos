from pathlib import Path
import sqlalchemy as sql
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from artistic.db import db
from artistic.models.base import Base

ROOT = Path(__file__).parent.parent
FILE_PATH = ROOT.joinpath('temp')
STATIC_PATH = ROOT.joinpath('static')


class Palette(Base):
    __tablename__ = 'palettes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    hex_values = db.Column(ARRAY(sql.String(128)))
    name = db.Column(db.String(128))

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_id': self.image_id,
            'name': self.name,
            'hex_values': self.hex_values,
            }
