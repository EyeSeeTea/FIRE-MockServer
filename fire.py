#!/usr/bin/env python
from datetime import datetime
import functools

from flask import Flask, jsonify, make_response, request, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS, cross_origin

import models

# JSON Responses

def success(data=None):
    json = dict(status="success", data=data)
    return jsonify(dict((k, v) for (k, v) in json.items() if v is not None))

def error(status_code, message):
    return make_response(jsonify(dict(status="error", message=message)), status_code)

def abort_with_error(status_code, message):
    abort(error(status_code, message))

# Auth

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    users_by_username = {user["username"]: user for user in models.users.values()}
    user = users_by_username.get(username)
    return (user["password"] if user else None)

@auth.error_handler
def unauthorized():
    return error(401, "Unauthorized access")

def get_current_user():
    auth_username = auth.username()
    user = first(user for user in models.users.values() if user["username"] == auth_username)
    if not user:
        abort_with_error(500, "Cannot get current user")
    else:
        return user

def admin_or_user(user_id):
    current_user = get_current_user()
    return (current_user["admin"] or current_user["id"] == user_id)

# Init flask app

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['ERROR_404_HELP'] = False

@app.errorhandler(404)
def page_not_found(exception):
    return error(404, "The requested URL was not found on the server")

def admin_required(arg=None):
    def wrapper(f):
        @functools.wraps(f)
        @auth.login_required
        def wrapped(*args, **kwargs):
            current_user = get_current_user()
            if current_user["admin"]:
                return f(*args, **kwargs)
            else:
                return unauthorized()
        return wrapped
    return (wrapper(arg) if callable(arg) else wrapper)

# Helper functions

def first(it):
    return next(it, None)

def merge(d1, d2):
    d3 = d1.copy()
    d3.update(d2)
    return d3

def get_user(users, user_id):
    if user_id not in models.users:
        abort_with_error(404, "User with id {} doesn't exist".format(user_id))
    else:
        return models.users[user_id]

# Resources

class NewUserRequestList(Resource):
    @admin_required
    def get(self):
        return success(list(models.new_user_requests.values()))

    def post(self):
        new_user = request.get_json().get("user")
        username = new_user.get("username")
        existing_usernames = (user["username"] for user in models.users.values())
        pending_requested_usernames = (req["user"]["username"]
            for req in models.new_user_requests.values() if req["state"] == "pending")

        if not username:
            return error(400, "Missing field: username")
        if username in existing_usernames:
            return error(400, "User {} already exist".format(username))
        elif username in pending_requested_usernames:
            return error(400, "There is a request for user {} already pending".format(username))
        else:
            new_id = models.get_next_id(models.new_user_requests)
            new_user_request = {
                "id": new_id,
                "user": models.get_public_user(new_user),
                "created": datetime.now(),
                "updated": datetime.now(),
                "adminUser": None,
                "state": "pending",
            }
            models.new_user_requests[new_id] = new_user_request
            return success(new_user_request)

class CurrentUser(Resource):
    @auth.login_required
    def get(self):
        current_user = get_current_user()
        return success(models.get_public_user(current_user))

class UserList(Resource):
    @admin_required
    def get(self):
        return success([models.get_public_user(user) for user in models.users.values()])

class User(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = get_user(models.users, user_id)
        return success(models.get_public_user(models.users[user_id]))

    @admin_required
    def delete(self, user_id):
        user = get_user(models.users, user_id)
        del models.users[user_id]
        return success()

    @admin_required
    def patch(self, user_id):
        user = get_user(models.users, user_id)
        existing_user = models.users[user_id]
        request_user = request.get_json()
        new_user = dict(existing_user, **request_user)
        models.users[user_id] = new_user
        return success(new_user)

class NotificationList(Resource):
    @admin_required
    def get(self):
        return success(list(models.notifications.values()))

class NewUserRequestAcceptation(Resource):
    @admin_required
    def post(self, new_user_request_id):
        new_user_request = models.new_user_requests[new_user_request_id]
        if new_user_request["state"] != "accepted":
            new_user_request["state"] = "accepted"
            new_user_request["adminUser"] = get_current_user()
            new_user = new_user_request["user"]
            new_user_id = new_user.get("id", models.get_next_id(models.users))
            new_user["id"] = new_user_id
            new_user["state"] = "active"
            models.users[new_user_id] = new_user
            return success(new_user_request)
        else:
            return error(400, "newUserRequest {} already accepted".format(new_user_request_id))

class NewUserRequestRejection(Resource):
    @admin_required
    def post(self, new_user_request_id):
        new_user_request = models.new_user_requests[new_user_request_id]
        if new_user_request["state"] != "rejected":
            new_user_request["state"] = "rejected"
            new_user_request["adminUser"] = get_current_user()
            new_user_id = new_user_request["user"].get("id")
            models.users.pop(new_user_id, None)
            return success(new_user_request)
        else:
            return error(400, "newUserRequest {} already rejected".format(new_user_request_id))

class MessageList(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = get_user(models.users, user_id)
        user_messages = [m for m in models.messages.values() if m["toUser"]["id"] == user_id]
        return success(user_messages)

    @admin_required
    def post(self, user_id):
        user = get_user(models.users, user_id)
        new_message_base = request.get_json()
        new_message_id = models.get_next_id(models.messages)

        new_message = merge(new_message_base, {
            "id": new_message_id,
            "fromUser": get_current_user(),
            "toUser": user,
            "created": datetime.now()
        })
        models.messages[new_message_id] = new_message
        return success(new_message)

class CallPricing(Resource):
    @auth.login_required
    def get(self, number):
        return success(models.call_pricing)

class UserVoucherList(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = get_user(models.users, user_id)
        user_vouchers = [v for v in models.vouchers.values()
            if v["user"] and v["user"]["id"] == user["id"]]
        return success(user_vouchers)

    @auth.login_required
    def post(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = get_user(models.users, user_id)
        code = request.get_json()["code"]
        voucher = first(v for v in models.vouchers.values()
                if v["code"] == code and v["state"] == "inactive")
        if not voucher:
            return error(404, "Voucher with code {} not found".format(code))
        else:
            activated_voucher = merge(voucher, {
                "state": "active",
                "activated": datetime.now(),
                "user": models.get_public_user(user),
            })
            models.vouchers[voucher["id"]] = activated_voucher
            return success(activated_voucher)

class Pricing(Resource):
    @admin_required
    def get(self):
        return models.pricing

    @admin_required
    def patch(self):
        new_pricing = request.get_json()
        models.pricing.update(new_pricing)
        return success(models.pricing)

# Routes

## User not logged-in

api.add_resource(NewUserRequestList, '/newUserRequests')

## Admin

### Notifications

api.add_resource(NotificationList, '/notifications')
api.add_resource(NewUserRequestAcceptation, '/newUserRequests/<int:new_user_request_id>/acceptation')
api.add_resource(NewUserRequestRejection, '/newUserRequests/<int:new_user_request_id>/rejection')

### Users

api.add_resource(CurrentUser, '/currentUser')
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<int:user_id>')
api.add_resource(MessageList, '/users/<int:user_id>/messages')

### Billing

api.add_resource(Pricing, '/pricing')

### WifiCall

api.add_resource(CallPricing, '/callPricing/<string:number>')

### Vouchers

api.add_resource(UserVoucherList, '/users/<int:user_id>/vouchers')


if __name__ == '__main__':
    app.run(debug=True)