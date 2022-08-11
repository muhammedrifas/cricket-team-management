from flask import request

from db import db
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from resources.user import UserModel

from sqlalchemy.ext.mutable import MutableList

pickle_type = MutableList.as_mutable(db.PickleType())


class GameModel(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80), nullable=False)
    players = db.Column(pickle_type, nullable=True)

    def __init__(self, date):
        self.date = date
        self.players = None

    def add_player(self, player):
        if not self.players:
            self.players = []
        self.players.extend([player])
        self.save()

    def json(self):
        return {
            'id': self.id,
            'date': self.date,
            'players': [] if not self.players else [player.json() for player in self.players if player]
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def refresh_players(self):
        if self.players:
            names = [player.name for player in self.players]
            for i in range(len(names)):
                self.players[i] = UserModel.find_by_name(names[i])
            self.players = [player for player in self.players if player]
            self.save()

    @classmethod
    def find_by_date(cls, date):
        game = cls.query.filter_by(date=date).first()
        if game:
            game.refresh_players()
        return game


class GameResource(Resource):

    @jwt_required()
    def post(self, date):
        game = GameModel.find_by_date(date)
        if game:
            return {'message': 'Game with date {} already exists'.format(date)}, 400
        game_model = GameModel(date)
        game_model.save()
        return game_model.json(), 201

    def get(self, date):
        game = GameModel.find_by_date(date)
        if game:
            return game.json()
        return {'message': 'Game not found'}, 404

    @jwt_required()
    def put(self, date):
        game = GameModel.find_by_date(date)
        if game:
            game.delete()
        game = GameModel(date)
        players = request.get_json()['players']
        notfound = []
        for name in players:
            player = UserModel.find_by_name(name)
            if player:
                game.add_player(player)
            else:
                notfound.append(name)
        game.save()
        return {'message': 'Game updated', 'players not found': notfound}, 200

    @jwt_required()
    def patch(self, date):
        game = GameModel.find_by_date(date)
        if not game:
            return {'message': 'Game not found'}, 404
        cost = float(request.get_json()['cost'])
        if game.players:
            for i in range(len(game.players)):
                if game.players[i].played_games_ids:
                    if game.id in game.players[i].played_games_ids:
                        continue
                game.players[i].update_balance(-cost, game.id)
            game.refresh_players()
        game.save()

        return {'message': 'Success!'}, 200

    @jwt_required()
    def delete(self, date):
        game = GameModel.find_by_date(date)
        if game:
            game.delete()
            return {'message': 'Game deleted'}, 200
        return {'message': 'Game not found'}, 404


class GameListResource(Resource):
    def get(self):
        for game in GameModel.query.all():
            game.refresh_players()
        return {'games': [game.json() for game in GameModel.query.all()]}
