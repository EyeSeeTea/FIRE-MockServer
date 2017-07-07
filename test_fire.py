import unittest
import json
import collections
import importlib
from pprint import pprint
from datetime import datetime
from base64 import b64encode

from flask import jsonify

import fire

class TestFireApi(unittest.TestCase):
    Response = collections.namedtuple("Response", ["status", "body"])

    USERS = {
        "joel": {"id": 1, "username": "joel", "password": "joel1234"},
        "maggie": {"id": 2, "username": "maggie", "password": "maggie1234"},
        "marilyn": {"id": 3, "username": "marilyn", "password": "marilyn1234"},
    }

    def setUp(self):
        importlib.reload(fire.models)
        self.app = fire.app.test_client()

    def request(self, method, path, data=None, user=None):
        app_method = method.lower()
        if data:
            kwargs1 = {"data": json.dumps(data), "content_type": 'application/json'}
        else:
            kwargs1 = {}
        if user:
            encoded_password = b64encode(bytes(user["username"] + ':' + user["password"], "utf-8"))
            kwargs2 = {"headers": {'Authorization': 'Basic ' + encoded_password.decode("ascii")}}
        else:
            kwargs2 = {}
        kwargs = dict(kwargs1, **kwargs2)
        stream_response = getattr(self.app, app_method)(path, **kwargs)
        status = stream_response.status_code
        body = json.loads(stream_response.get_data(stream_response))
        return self.Response(status, body)

    ### Notifications

    def test_get_notifications_as_admin(self):
        res = self.request("GET", '/notifications', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        notifications = res.body
        self.assertEqual(len(notifications), 5)

    ### New User Requests

    def test_get_new_user_requests_as_admin(self):
        res = self.request("GET", '/newUserRequests', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        new_user_requests = res.body
        self.assertEqual(len(new_user_requests), 2)

    def test_get_new_user_requests_as_non_admin(self):
        res = self.request("GET", '/newUserRequests', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 401)

    def test_get_new_user_requests_unlogged(self):
        res = self.request("GET", '/newUserRequests')
        self.assertEqual(res.status, 401)

    def test_post_new_user_requests(self):
        new_user = {
            "name": "Joel Fleischman",
            "username": "joel2",
            "address": "Flushing, Queens (New York City)",
            "gender": "male",
            "avatarUrl" : "http://24.media.tumblr.com/tumblr_lrt2nf1G7Y1qh4q2fo4_500.png",
            "email": "joel.fleischman@mail.com",
            "state": "active",
            "phoneNumber": "123-123-001",
            "created": '2017-04-27T16:10:11.894490',
            "lastAccess": '2017-04-27T16:10:11.894490',
            "serverHost": "http://pbx.com/provision",
        }
        res = self.request("POST", '/newUserRequests', {"user": new_user})
        self.assertEqual(res.status, 200, "Body: {}".format(res.body))
        new_user_request = res.body
        self.assertTrue("adminUser" in new_user_request)
        self.assertIsNone(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["state"], "pending")
        response_user = {k: v for (k, v) in new_user_request["user"].items() if k in new_user}
        self.assertEqual(response_user, new_user)

    def test_post_new_user_requests_acceptation(self):
        res = self.request("POST", '/newUserRequests/1/acceptation', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        new_user_request = res.body.get("new_user_request")
        self.assertTrue(new_user_request)
        self.assertTrue(new_user_request.get("id"))
        self.assertEqual(new_user_request["state"], "accepted")
        self.assertTrue(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["adminUser"]["id"], self.USERS["joel"]["id"])

    def test_post_new_user_requests_acceptation_on_already_accepted_request(self):
        res = self.request("POST", '/newUserRequests/2/acceptation', user=self.USERS["joel"])
        self.assertEqual(res.status, 400)

    def test_post_new_user_requests_rejection(self):
        res = self.request("POST", '/newUserRequests/1/rejection', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        new_user_request = res.body.get("new_user_request")
        self.assertTrue(new_user_request)
        self.assertTrue(new_user_request["id"])
        self.assertEqual(new_user_request["state"], "rejected")
        self.assertTrue(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["adminUser"]["id"], self.USERS["joel"]["id"])

    # Users

    def test_get_current_user_succeeds(self):
        res = self.request("GET", '/currentUser', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 200)
        users = res.body
        self.assertEqual(users["username"], "marilyn")

    def test_get_current_user_without_auth_is_not_authorized(self):
        res = self.request("GET", '/currentUser')
        self.assertEqual(res.status, 401)

    def test_get_users_as_admin_succeeds(self):
        res = self.request("GET", '/users', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        self.assertEqual(len(res.body), 3)

    def test_get_users_as_non_admin_is_not_authorized(self):
        res = self.request("GET", '/users', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 401)

    def test_get_own_user_as_admin_succeeds(self):
        res = self.request("GET", '/users/1', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)

    def test_get_other_user_as_admin_succeeds(self):
        res = self.request("GET", '/users/2', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)

    def test_get_own_user_as_user_succeeds(self):
        res = self.request("GET", '/users/3', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 200)

    def test_get_other_user_as_user_is_not_authorized(self):
        res = self.request("GET", '/users/1', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 401)

    def test_patch_user(self):
        data = {"email": "newemail1@mail.com"}
        res = self.request("PATCH", '/users/1', data=data, user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        self.assertEqual(res.body["email"], "newemail1@mail.com")

    def test_delete_user(self):
        res = self.request('DELETE', '/users/2', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)

        res = self.request('GET', '/users/2', user=self.USERS["joel"])
        self.assertEqual(res.status, 404)

    # Messages

    def test_get_user_messages_as_admin(self):
        res = self.request("GET", '/users/3/messages', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        self.assertEqual(len(res.body), 2)
        self.assertTrue(all(message["toUser"]["id"] == 3 for message in res.body))

    def test_get_user_messages_as_recipient(self):
        res = self.request("GET", '/users/3/messages', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 200)
        self.assertEqual(len(res.body), 2)
        self.assertTrue(all(message["toUser"]["id"] == 3 for message in res.body))

    def test_get_user_messages_as_normal_user_to_another_user(self):
        res = self.request("GET", '/users/1/messages', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 401)

    def test_post_user_message(self):
        post_message = {"text": "Hello there!"}
        res = self.request("POST", '/users/3/messages', data=post_message, user=self.USERS["joel"])
        self.assertEqual(res.status, 200, "Body: {}".format(res.body))
        message = res.body
        self.assertEqual(message["text"], "Hello there!")
        self.assertEqual(message["fromUser"].get("id"), 1)
        self.assertEqual(message["toUser"].get("id"), 3)

    # Pricing

    def test_get_pricing(self):
        res = self.request("GET", '/pricing', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)

    def test_patch_pricing(self):
        post_pricing = {
            "localMobile": 1.55,
            "localLandLines": 0.85,
        }
        res = self.request("PATCH", '/pricing', data=post_pricing, user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        pricing = res.body
        self.assertEqual(pricing["localMobile"], 1.55)
        self.assertEqual(pricing["localLandLines"], 0.85)
        self.assertEqual(pricing["nationalLandLines"], 2.1)
        self.assertEqual(pricing["nationalMobile"], 2.3)

    # Call Pricing

    def test_get_call_pricing(self):
        res = self.request("GET", '/callPricing/123-123-123', user=self.USERS["joel"])
        self.assertEqual(res.status, 200)
        pricing = res.body
        self.assertEqual(pricing["gsm"], 1.5)
        self.assertEqual(pricing["voip"], 0.01)

    # Vouchers

    def test_get_user_vouchers(self):
        res = self.request("GET", '/users/3/vouchers', user=self.USERS["marilyn"])
        self.assertEqual(res.status, 200)
        vouchers = res.body
        self.assertEqual(len(vouchers), 1)
        self.assertTrue(all(message["user"]["id"] == 3 for message in res.body))

    def test_post_user_voucher_with_code_of_inactive(self):
        post_voucher = {"code": "voucher3"}
        res = self.request("POST", '/users/3/vouchers', data=post_voucher, user=self.USERS["marilyn"])
        self.assertEqual(res.status, 200, "Body: {}".format(res.body))
        voucher = res.body
        self.assertEqual(voucher["user"].get("id"), 3)

    def test_post_user_voucher_with_code_of_already_active(self):
        post_voucher = {"code": "voucher1"}
        res = self.request("POST", '/users/3/vouchers', data=post_voucher, user=self.USERS["marilyn"])
        self.assertEqual(res.status, 404, "Body: {}".format(res.body))


if __name__ == "__main__":
    unittest.main()