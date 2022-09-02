import os
from datetime import timedelta

from flask import Flask, render_template, jsonify
from flask_jwt import JWT
from flask_restful import Api

from resources.images import *

from resources.user import *
from resources.admin import *
from resources.game import *
from security import *
from resources.tokenvalidation import *
from db import db

app = Flask(__name__)
app.secret_key = '####'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=60000)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')
api = Api(app)

jwt = JWT(app, authenticate, identity)

api.add_resource(UserResource, '/user/<string:name>')
api.add_resource(GameResource, '/game/<string:date>')
api.add_resource(ListUsersResource, '/users/')
api.add_resource(GameListResource, '/games/')
api.add_resource(DumpUsersResource, '/csv/')
api.add_resource(TokenValidation, '/token_validation/')
api.add_resource(UserImageResource, '/userimages/<string:name>')
api.add_resource(GalleryImageResource, '/gallery/')


# set index.html as root
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/player/<string:name>/')
def player(name):
    user = UserModel.find_by_name(name)
    if user:
        import resources.images as images
        avatar = images.ImageModel.find_user_image_by_name(name)
        if avatar:
            avatar_url = avatar.media_url
        else:
            avatar_url = images.DEFAULT_AVATAR
        return render_template('player_profile.html', avatar_url=avatar_url, name=name.upper(),
                               balance='{:,.2f}'.format(user.balance))
    return jsonify({'message': 'User not found'}), 404


@app.route('/players/')
def players():
    lst = [user for user in UserModel.query.order_by(UserModel.balance).all()]
    # use player_profile.html as template for EACH player and combine the results and return HTML
    result = ""
    for player in lst:
        image = ImageModel.find_user_image_by_name(player.name)
        if image:
            avatar_url = image.media_url
        else:
            avatar_url = DEFAULT_AVATAR
        result += render_template('player_profile.html', avatar_url=avatar_url, name=player.name.upper(),
                                  balance='{:,.2f}'.format(player.balance))
    return result, 200


@app.route('/games_html/')
def games_html():
    lst = [game for game in GameModel.query.order_by(GameModel.date.desc()).all()]
    result = ""
    for game in lst:
        date = convert_date(game.date)
        players = []
        for player in game.players:
            image = ImageModel.find_user_image_by_name(player.name)
            if image:
                avatar_url = image.media_url
            else:
                avatar_url = DEFAULT_AVATAR
            name = player.name.upper()
            players.append((avatar_url, name))
        result += render_template('game_details.html', date=date, players=players, count=len(players))
    return result, 200


if __name__ == '__main__':
    db.init_app(app)
    db.create_all(app=app)
    app.run(port=5000, debug=True)
