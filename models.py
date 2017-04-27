from datetime import datetime

def get_public_user(user, private_fields=["password"]):
    return {k: v for (k, v) in user.items() if k not in private_fields}

def user(user_id):
    return get_public_user(users[user_id])

users = {
    1: {
        "id": 1,
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
        "password": "joel1234",
    },
    2: {
        "id": 2,
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
        "password": "maggie1234",
    },
    3: {
        "id": 3,
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
        "password": "marilyn1234",
    },
}

new_user_requests = {
    1: {
        "id": 1,
        "user": user(3),
        "created": datetime(2014, 1, 2),
        "updated": datetime(2014, 1, 2),
        "adminUser": None,
        "state": "pending",
    },
    2: {
        "id": 1,
        "user": user(2),
        "created": datetime(2015, 1, 2),
        "updated": datetime(2015, 1, 2),
        "adminUser": user(1),
        "state": "accepted",
    },
}

messages = {
    1: {
        "id": 1,
        "text": "Were you able to call?",
        "fromUser": user(1),
        "toUser": user(3),
        "created": datetime(2016, 7, 26, 22, 10),
    },
    2: {
        "id": 2,
        "text": "Make sure you have credit before making a call",
        "fromUser": user(1),
        "toUser": user(3),
        "created": datetime(2016, 7, 26, 22, 50),
    },
}

vouchers = {
    1: {
        "id": 1,
        "user": user(1),
        "state": "active",
        "creditRemaining": 40,
        "creditTotal": 50,
        "code": "voucher1",
        "url": "http://vouchers/50",
        "bulkNumber": "bulk-50",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": datetime(2016, 7, 26, 23, 50),
        "depleted": None,
    },
    2: {
        "id": 2,
        "user": user(3),
        "state": "depleted",
        "creditRemaining": 0,
        "creditTotal": 80,
        "code": "voucher2",
        "url": "http://vouchers/80",
        "bulkNumber": "bulk-80",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": datetime(2016, 7, 26, 23, 50),
        "depleted": datetime(2016, 7, 29, 20, 50),
    },
    3: {
        "id": 3,
        "user": None,
        "state": "inactive",
        "creditRemaining": 70,
        "creditTotal": 70,
        "code": "voucher3",
        "url": "http://vouchers/3",
        "bulkNumber": "bulk-80",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": None,
        "depleted": None,
    },
}

notifications = {
    1: {
        "type": "newUserAccepted",
        "newUserRequest": new_user_requests[2],
    },
    2: {
        "type": "newUserRequest",
        "newUserRequest": new_user_requests[1],
    },
    3: {
        "type": "messageSent",
        "message": messages[1],
    },
    4: {
        "type": "profileUpdated",
        "user": user(2),
    },
    5: {
        "type": "toppedUp",
        "voucher": vouchers[1],
    },
}

pricing = {
    "localMobile": 1.5,
    "localLandLines": 0.8,
    "nationalMobile": 2.3,
    "nationalLandLines": 2.1,
    "international": [
        {
            "country": "Sierra Leone",
            "mobile": 8.4,
            "landLines": 5.3,
        },
        {
            "country": "Rwanda",
            "mobile": 9.2,
            "landLines": 6.3,
        },
    ]
}

call_pricing = {
    "gsm": 1.5,
    "voip": 0.01,
}
