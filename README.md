# Introduction

Mock server for FIRE.

# Setup

```
$ git clone git@github.com:EyeSeeTea/FIRE-MockServer.git
$ cd FIRE-MockServer
$ virtualenv -p /path/to/your/system/python3 env
$ env/bin/pip install -r requirements.txt
$ FLASK_APP=fire.py FLASK_DEBUG=1 .env/bin/flask run --host=127.0.0.1
```

# Example of usage 

See the [example models](models.py) to see the available users and other resources.

You can use `curl` with basic authentication (`-u user:password`, see `models.users`). 

* Get the list of users:

```
$ curl -u joel:joel1234 -sS http://localhost:5000/users -X GET
{...}
```

* Send a message to a user:

```
$ curl -u joel:joel1234 -sS http://localhost:5000/users/3/messages \
  -X POST -H "Content-Type: application/json" \
  -d '{"text": "Hello there"}'
```

# App actions

## Pre-login

- POST /newUserRequests : NewUserRequest -> STATUS

## Admin

### Notifications

- GET /notifications -> [Notification]

- POST /newUserRequests/{id}/acceptation -> STATUS
- POST /newUserRequests/{id}/rejection -> STATUS

### Users

- GET /users -> [User]
- GET /users/{id} -> User
- PATCH /users/{id} User -> STATUS
- DELETE /users/{id} -> STATUS

- GET /users/{id}/messages -> [Message]
- POST /users/{id}/messages : Message -> STATUS

### Billing

- GET /pricing -> Pricing
- PATCH /pricing : Pricing -> STATUS

## WifiCall

### Call

- GET /callPricing/{number} -> callPricing

### Top Up

- GET /users/{id}/vouchers -> [Voucher]
- POST /users/{id}/vouchers : Voucher -> STATUS

## Settings

- PATCH /users/{id} : User -> STATUS

# Models

## NewUserRequest

- id: Int
- user: User
- created: Date
- updated: Date
- adminUser: User
- state: String ("pending" | "accepted" | "rejected")

## User

- id: Int
- name: String
- username: String
- address: String
- avatarUrl: String
- email: String
- gender: String ("male" | "female")
- state: String ("pending" | "active")
- phoneNumber: String
- created: Date
- updated: Date
- lastAccess: Date

## Notifications

- id: Int
- created: Date
- seen: Bool
- type: String
  - "newUserRequest". Extra fields:
    - newUserRequest: NewUserRequest
  - "newUserAccepted". Extra fields:
    - newUserRequest: NewUserRequest
  - "messageSent". Extra fields:
    - message: Message
  - "profileUpdated". Extra fields:
    - user: User
  - "toppedUp". Extra fields:
    - voucher: Voucher

## Message

- id: Int
- fromUser: User
- toUser: User
- text: String
- created: Date

## Voucher

- id: Int
- user: User
- state: String ("inactive" | "active" | "depleted")
- creditRemaining: Number
- creditTotal: Number
- code: String
- url: String
- bulkNumber: String
- Vendor: String
- created: Date
- activated: Date
- depleted: Date

## Pricing

- localMobile: Number
- localLandLines: Number
- nationalMobile: Number
- nationalLandLines: Number
- international (List): 
  - country: String
  - mobile: Number
  - landLines: Number

## CallPricing

- gsm: Number
- voip: Number
