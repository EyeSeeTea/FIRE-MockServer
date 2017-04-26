from datetime import datetime

from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api, abort, reqparse

# https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html
# https://blog.miguelgrinberg.com/post/restful-authentication-with-flask

app = Flask(__name__)
app.config['ERROR_404_HELP'] = False
api = Api(app)

users = {
    "1": {
        "id": "1",
        "name": "Joel Fleischman",
        "username": "joel",
        "address": "Flushing, Queens (New York City)",
        "admin": True,
        "gender": "male",
        "avatarUrl" : "http://24.media.tumblr.com/tumblr_lrt2nf1G7Y1qh4q2fo4_500.png",
        "email": "joel.fleischman@mail.com",
        "state": "active",
        "phoneNumber": "123-123-001",
        "created": datetime(2016, 4, 20),
        "lastAccess": datetime(2016, 4, 24),
        "serverHost": "http://pbx.com/provision",
        "password_hash": "1234",
    },
    "2": {
        "id": "2",
        "name": "Maggie O'Connell",
        "username": "maggie",
        "address": "Cicely, Alaska",
        "admin": True,
        "gender": "female",
        "avatarUrl" : "https://s-media-cache-ak0.pinimg.com/736x/ab/e9/33/abe93316032b2eb1c0f0a28d0761247d.jpg",
        "email": "maggie.oconnell@mail.com",
        "state": "pending",
        "phoneNumber": "123-123-002",
        "created": datetime(2016, 5, 10),
        "lastAccess": datetime(2016, 5, 14),
        "serverHost": "http://pbx.com/provision",
        "password_hash": "1234",
    },
    "3": {
        "id": "3",
        "name": "Marilyn Whirlwind",
        "username": "marilyn",
        "address": "Cicely, Alaska",
        "admin": False,
        "gender": "female",
        "avatarUrl" : "http://www.moosechick.com/Marilyn-totem.JPG",
        "email": "marilyn.whildwind@mail.com",
        "state": "active",
        "phoneNumber": "123-123-003",
        "created": datetime(2014, 1, 2),
        "lastAccess": datetime(2016, 7, 26),
        "serverHost": "http://pbx.com/provision",
        "password_hash": "1234",
    },
}

messages = {
    "1": {
        "text": "Were you able to call?",
        "from": users["1"],
        "to": users["3"],
        "sent": datetime(2016, 7, 26, 22, 10),
    },
    "2": {
        "text": "Make sure you have credit before making a call",
        "from": users["1"],
        "to": users["3"],
        "sent": datetime(2016, 7, 26, 22, 50),
    },
}

vouchers = {
    "1": {
        "user": users["3"],
        "state": "active",
        "creditRemaining": 40,
        "creditTotal": 50,
        "code": "voucher50",
        "url": "http://vouchers/50",
        "bulkNumber": "bulk-50",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": datetime(2016, 7, 26, 23, 50),
        "assigned": datetime(2016, 7, 27, 20, 50),
        "depleted": None,
    },
}

notifications = {
    "1": {
        "type": "newUserAccepted",
        "user": users["1"],
    },
    "2": {
        "type": "newUserAccepted",
        "admin": users["1"],
        "user": users["3"],
    },
    "3": {
        "type": "newUserRequest",
        "admin": users["1"],
        "user": users["2"],
    },
    "4": {
        "type": "messageSent",
        "message": messages["1"],
    },
    "5": {
        "type": "profileUpdated",
        "user": users["2"],
    },
    "6": {
        "type": "toppedUp",
        "voucher": vouchers["1"],
    },
}

def get_public_user(user, private_fields=["password_hash"]):
    return {k: v for (k, v) in user.items() if k not in private_fields}

parser = reqparse.RequestParser()
parser.add_argument('user')

class UserList(Resource):
    def get(self):
        return jsonify([get_public_user(user) for user in users.values()])

class User(Resource):
    def get(self, user_id):
        if user_id not in users:
            abort(404, message="User with id {} doesn't exist".format(user_id))
        else:
            return jsonify(get_public_user(users[user_id]))

    def patch(self, user_id):
        if user_id not in users:
            abort(404, message="User with id {} doesn't exist".format(user_id))
        else:
            existing_user = users[user_id]
            request_user = request.json
            new_user = dict(existing_user, **request_user)
            users[user_id] = new_user
            return make_response(jsonify(new_user), 201)

class NotificationList(Resource):
    def get(self):
        return jsonify(list(notifications.values()))


api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:user_id>')

api.add_resource(NotificationList, '/notifications')

if __name__ == '__main__':
    app.run(debug=True)