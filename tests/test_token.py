#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import unittest
from datetime import datetime

import requests
import json
from pymongo import MongoClient


DOMAIN = 'http://127.0.0.1:5000'


class TestBase(unittest.TestCase):

    TOKEN_URI = DOMAIN + '/tokens/'
    USER_URI = DOMAIN + '/users/'

    def setUp(self):
        self.db = MongoClient().test

        self.db.user.insert({
            'username': 'russell',
            'password': '123456',
            'date_joined': datetime(2014, 10, 25),
            'jwt_secret': str(uuid.uuid4())
        })

        self.headers = {'content-type': 'application/json'}

    def tearDown(self):
        self.db.user.remove()

    def login(self, username, password):
        data = {
            'username': username,
            'password': password,
        }
        resp = requests.post(self.TOKEN_URI, data=json.dumps(data),
                             headers=self.headers)
        return resp

    def logout(self, id, token):
        resp = requests.delete('%s%s/' % (self.TOKEN_URI, id),
                               auth=(token, ''))
        return resp


class TokenTest(TestBase):

    def test_login_with_valid_credentials(self):
        resp = self.login('russell', '123456')
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertNotEqual(data['token'], None)
        self.assertEqual(data['expires'], 3600)

    def test_login_with_invalid_credentials(self):
        resp = self.login('russell', 'wrong_password')
        self.assertEqual(resp.status_code, 400)

        data = resp.json()
        self.assertEqual(data['errors'], 'username or password is wrong')

    def test_logout_without_token(self):
        token = self.login('russell', '123456').json()

        # logout without auth-token
        resp = self.logout(token['id'], '')
        self.assertEqual(resp.status_code, 401)

    def test_logout_with_wrong_tokenid(self):
        token = self.login('russell', '123456').json()

        # logout with wrong token-id
        resp = self.logout('1', token['token'])
        self.assertEqual(resp.status_code, 404)

    def test_logout_twice(self):
        token = self.login('russell', '123456').json()

        # the 1st logout
        resp = self.logout(token['id'], token['token'])
        self.assertEqual(resp.status_code, 204)

        # the 2nd logout, token is invalid
        resp = self.logout(token['id'], token['token'])
        self.assertEqual(resp.status_code, 401)


class UserTest(TestBase):

    def test_get_without_token(self):
        resp = requests.get(self.USER_URI)
        self.assertEqual(resp.status_code, 401)

    def test_get_with_invalid_token(self):
        resp = requests.get(self.USER_URI, auth=('anonymous', ''))
        self.assertEqual(resp.status_code, 401)

    def test_get_with_valid_token(self):
        token = self.login('russell', '123456').json()
        resp = requests.get(self.USER_URI, auth=(token['token'], ''))
        self.assertEqual(resp.status_code, 200)

    def test_get_login_logout(self):
        # after login, before logout, `token` is valid
        token = self.login('russell', '123456').json()
        resp = requests.get(self.USER_URI, auth=(token['token'], ''))
        self.assertEqual(resp.status_code, 200)

        # logout
        resp = self.logout(token['id'], token['token'])
        self.assertEqual(resp.status_code, 204)

        # after logout, `token` becomes invalid
        resp = requests.get(self.USER_URI, auth=(token['token'], ''))
        self.assertEqual(resp.status_code, 401)

    def test_post(self):
        """Everyone can POST."""
        data = {
            'username': 'tracey',
            'password': '123456',
            'date_joined': 'datetime(2014-10-25T00:00:00Z)'
        }
        resp = requests.post(self.USER_URI, data=json.dumps(data),
                             headers=self.headers)

        self.assertEqual(resp.status_code, 201)


if __name__ == '__main__':
    unittest.main()
