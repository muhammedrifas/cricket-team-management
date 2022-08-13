from flask import request

from db import db
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from sqlalchemy.ext.mutable import MutableList

pickle_type = MutableList.as_mutable(db.PickleType())


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float(precision=2))
    played_games_ids = db.Column(pickle_type, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_balance(self, amount, game_id=None):
        self.balance += amount
        if game_id:
            if not self.played_games_ids:
                self.played_games_ids = []
            self.played_games_ids.extend([game_id])
        self.save()

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance
            # 'played_games_ids': [] if not self.played_games_ids else [game_id for game_id in self.played_games_ids]
        }

    def __init__(self, name, balance=0.0):
        self.name = name.lower()
        self.balance = balance
        self.played_games_ids = None

    @classmethod
    def find_by_name(cls, name):
        name = name.lower()
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def return_csv(cls):
        data = 'name,balance\n'
        for user in cls.query.order_by(cls.name).all():
            data += f'{user.name},{user.balance}\n'
        return data


class UserResource(Resource):
    def get(self, name):
        user = UserModel.find_by_name(name)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404

    @jwt_required()
    def post(self, name):
        if UserModel.find_by_name(name):
            return {'message': 'User with name {} already exists'.format(name)}, 400
        user = UserModel(name)
        user.save()
        return {'message': 'User created successfully'}, 201

    @jwt_required()
    def patch(self, name):
        user = UserModel.find_by_name(name)
        if not user:
            return {'message': 'User not found'}, 404
        amount = float(request.json.get('amount'))
        user.update_balance(amount)
        return {'message': 'User balance updated successfully'}, 200


class ListUsersResource(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.query.order_by(UserModel.balance).all()]}


class DumpUsersResource(Resource):
    def get(self):
        return {'csv': UserModel.return_csv()}, 200
