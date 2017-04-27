import unittest
import json
import collections
import importlib
from pprint import pprint
from datetime import datetime
from base64 import b64encode

from flask import jsonify

import fire



class TestFlaskApi(unittest.TestCase):
    Response = collections.namedtuple("Response", ["status", "body"])
    USERS = {
        "joel": {"username": "joel", "password": "joel1234"},
    }

    def setUp(self):
        importlib.reload(fire.models)
        self.app = fire.app.test_client()

    def request(self, method, path, data=None, user=None):
        app_method = method.lower()
        if data:
            kwargs1 = {
                "data": json.dumps(data), 
                "content_type": 'application/json',
            }
        else:
            kwargs1 = {}
        if user:
            encoded_password = b64encode(bytes(user["username"] + ':' + user["password"], "utf-8")).decode("ascii")
            kwargs2 = {
                "headers": {
                    'Authorization': 'Basic ' + encoded_password,
                }
            }        
        else:
            kwargs2 = {}
        kwargs = dict(kwargs1, **kwargs2)
        stream_response = getattr(self.app, app_method)(path, **kwargs)
        status = stream_response.status_code
        body = json.loads(stream_response.get_data(stream_response))
        return self.Response(status, body)

    def test_get_new_user_requests(self):
        res = self.request("GET", '/newUserRequests')
        self.assertEqual(res.status, 200)
        new_user_requests = res.body
        self.assertEqual(len(new_user_requests), 2)

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
        res = self.request("POST", '/newUserRequests/1/acceptation')
        self.assertEqual(res.status, 200)
        new_user_request = res.body.get("new_user_request")
        self.assertTrue(new_user_request)
        self.assertTrue(new_user_request["id"])
        self.assertEqual(new_user_request["state"], "accepted")

    def test_post_new_user_requests_acceptation_on_already_accepted_request(self):
        res = self.request("POST", '/newUserRequests/2/acceptation')
        self.assertEqual(res.status, 400)

    def test_post_new_user_requests_rejection(self):
        res = self.request("POST", 'newUserRequests/1/rejection')
        self.assertEqual(res.status, 200)
        r = res.body.get("new_user_request")
        self.assertTrue(r)
        self.assertTrue(r["id"])
        self.assertEqual(r["state"], "rejected")

    # Users

    def test_get_users(self):
        res = self.request("GET", '/users')
        self.assertEqual(res.status, 200)
        self.assertEqual(len(res.body), 3)

    def test_get_user(self):
        res = self.request("GET", '/users/1')
        self.assertEqual(res.status, 200)

    def test_patch_user(self):
        res = self.request("PATCH", '/users/1', {"email": "newemail1@mail.com"})
        self.assertEqual(res.status, 200)
        self.assertEqual(res.body["email"], "newemail1@mail.com")

    def test_delete_user(self):
        res = self.request('DELETE', '/users/1')
        self.assertEqual(res.status, 200)

        res = self.request('GET', '/users/1')
        self.assertEqual(res.status, 404)

    # Messages

    def test_get_user_messages(self):
        res = self.request("GET", '/users/3/messages')
        self.assertEqual(res.status, 200)
        self.assertEqual(len(res.body), 2)
        self.assertTrue(all(message["toUser"]["id"] == 3 for message in res.body))

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
        res = self.request("GET", '/pricing')
        self.assertEqual(res.status, 200)

    # Call Pricing

    def test_get_call_pricing(self):
        res = self.request("GET", '/callPricing/123-123-123')
        pricing = res.body
        self.assertEqual(pricing["gsm"], 1.5)
        self.assertEqual(pricing["voip"], 0.01)

    # Vouchers

    def test_get_user_vouchers(self):
        res = self.request("GET", '/users/3/vouchers')
        self.assertEqual(res.status, 200)
        vouchers = res.body
        self.assertEqual(len(vouchers), 1)
        self.assertTrue(all(message["user"]["id"] == 3 for message in res.body))

    def test_post_user_voucher_with_code_of_inactive(self):
        post_voucher = {"code": "voucher3"}
        res = self.request("POST", '/users/3/vouchers', post_voucher)
        self.assertEqual(res.status, 200, "Body: {}".format(res.body))
        voucher = res.body
        self.assertEqual(voucher["user"].get("id"), 3)

    def test_post_user_voucher_with_code_of_already_active(self):
        post_voucher = {"code": "voucher1"}
        res = self.request("POST", '/users/3/vouchers', post_voucher)
        self.assertEqual(res.status, 404, "Body: {}".format(res.body))


if __name__ == "__main__":
    unittest.main()