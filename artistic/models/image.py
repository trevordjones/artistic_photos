import binascii
from google.cloud import storage
import os
from pathlib import Path
from sqlalchemy.orm import relationship

from artistic.db import db
from artistic.models.base import Base

ROOT = Path(__file__).parent.parent
FILE_PATH = ROOT.joinpath('temp')
STATIC_PATH = ROOT.joinpath('static')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')


class Image(Base):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128))
    source_name = db.Column(db.String(128))
    subdirectory = db.Column(db.String(128))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    starting_image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    starting_image = relationship('Image', remote_side=[id])
    artistic_images = relationship('Image', lazy='dynamic')
    user = relationship('User')

    @classmethod
    def upload_to_gcp(cls, file, subdirectory, image_name):
        try:
            file_path = f'{FILE_PATH}/{file.filename}'
            file.save(file_path)
            storage_client = storage.Client()
            bucket_name = STORAGE_BUCKET
            bucket = storage_client.bucket(bucket_name)
            gcp_source_name = f'{image_name}-{file_path.split("/")[-1]}'
            destination_blob_name = f'{subdirectory}/{gcp_source_name}'
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            image = cls(
                source_name=gcp_source_name,
                subdirectory=subdirectory,
                name=image_name,
                )
            return image
        except:
            raise
        finally:
            os.remove(file_path)


    def save(self, **kwargs):
        self.__dict__.update(kwargs)
        db.session.add(self)
        db.session.commit()

    def download(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(STORAGE_BUCKET)
        file_name = f'{self.subdirectory}/{self.source_name}'
        download_blob = bucket.blob(file_name)
        to_file = STATIC_PATH.joinpath(f'img/{self.source_name}')
        download_blob.download_to_filename(to_file)

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'source_name': self.source_name,
            'subdirectory': self.subdirectory,
            'width': self.width,
            'height': self.height,
            'url': f'/artistic/static/img/{self.source_name}'
            }
        return {'id': self.id}
