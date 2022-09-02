from db import db
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from resources.user import UserModel


DEFAULT_AVATAR = "https://thumbsnap.com/i/LARfdMJe.png"


class ImageModel(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    media_url = db.Column(db.String(80), nullable=False)
    thumb_url = db.Column(db.String(80), nullable=False)
    is_user_image = db.Column(db.Boolean, default=False)

    def __init__(self, name, media_url, thumb_url, is_user_image):
        self.name = name
        self.media_url = media_url
        self.thumb_url = thumb_url
        self.is_user_image = is_user_image

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'media_url': self.media_url,
            'thumb_url': self.thumb_url,
            'is_user_image': self.is_user_image
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_user_image_by_name(cls, name):
        return cls.query.filter_by(name=name, is_user_image=True).first()

    @classmethod
    def find_gallery_images(cls):
        return cls.query.filter_by(is_user_image=False).all()



class UserImageResource(Resource):
    def get(self, name):
        image = ImageModel.find_user_image_by_name(name)
        if image:
            return {"media_url": image.media_url, "thumb_url": image.thumb_url}, 200
        return {"media_url": DEFAULT_AVATAR, "thumb_url": DEFAULT_AVATAR}, 200

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('media_url',
                            type=str,
                            required=True,
                            help="This field cannot be left blank!"
                            )
        parser.add_argument('thumb_url',
                            type=str,
                            required=True,
                            help="This field cannot be left blank!"
                            )
        data = parser.parse_args()
        image = ImageModel.find_user_image_by_name(name)
        if image:
            image.delete()
        image = ImageModel(name, data['media_url'], data['thumb_url'], True)
        try:
            image.save()
        except:
            return {"message": "An error occurred inserting the image."}, 500
        return {"message": "Image saved successfully."}, 200


class GalleryImageResource(Resource):
    def get(self):
        images = ImageModel.find_gallery_images()
        if images:
            return [image.json() for image in images]
        return {'message': 'No images found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name',
                            type=str,
                            required=True,
                            help="This field cannot be left blank!"
                            )
        parser.add_argument('media_url',
                            type=str,
                            required=True,
                            help="This field cannot be left blank!"
                            )
        parser.add_argument('thumb_url',
                            type=str,
                            required=True,
                            help="This field cannot be left blank!"
                            )
        data = parser.parse_args()

        image = ImageModel(data['name'], data['media_url'], data['thumb_url'], False)
        try:
            image.save()
        except:
            return {"message": "An error occurred inserting the image."}, 500
        return {"message": "Image saved successfully."}, 200
