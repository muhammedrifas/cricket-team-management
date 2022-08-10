import os
from datetime import timedelta

from flask import Flask, render_template
from flask_jwt import JWT
from flask_restful import Api

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




if __name__ == '__main__':
    db.init_app(app)
    db.create_all(app=app)
    app.run(port=5000, debug=True)
