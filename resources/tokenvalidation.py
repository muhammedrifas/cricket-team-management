from db import db
from flask_restful import Resource
from flask_jwt import jwt_required


class TokenValidation(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'valid JWT token'}, 200