from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

# # Configure MongoDB URI and database name
app.config['MONGO_URI'] = 'mongodb://localhost:27017/user_database'
app.config['MONGO_DB'] = 'user_database'

# Initialize PyMongo client and database
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo[app.config['MONGO_DB']]

# User resource fields: id, name, email, password
user_fields = ['name', 'email', 'password']

# Request parser for POST and PUT requests
parser = reqparse.RequestParser()
for field in user_fields:
    parser.add_argument(field, required=True)


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = db.users.find_one({'_id': ObjectId(user_id)}, {'_id': 0})
            if user:
                return user
            return {'message': 'User not found'}, 404
        else:
            users = list(db.users.find({}, {'_id': 0}))
            return users

    def post(self):
        args = parser.parse_args()
        user_id = db.users.insert_one(args).inserted_id
        new_user = db.users.find_one({'_id': user_id}, {'_id': 0})
        return new_user, 201

    def put(self, user_id):
        args = parser.parse_args()
        result = db.users.update_one({'_id': ObjectId(user_id)}, {'$set': args})
        if result.modified_count:
            updated_user = db.users.find_one({'_id': ObjectId(user_id)}, {'_id': 0})
            return updated_user
        return {'message': 'User not found'}, 404

    def delete(self, user_id):
        result = db.users.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count:
            return {'message': 'User deleted successfully'}
        return {'message': 'User not found'}, 404


api.add_resource(UserResource, '/users', '/users/<string:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
