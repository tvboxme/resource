#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from pymongo import MongoClient
from jsonform import JsonForm

from resource import Resource
from resource.db.mongo import Collection, MongoSerializer
from resource.framework.flask import add_resource


DB = MongoClient().test


class UserForm(JsonForm):
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'password': {'type': 'string'}
        }
    }


resources = [
    Resource('users', Collection, form=UserForm,
             serializer=MongoSerializer,
             kwargs={'engine': DB['user']})
]


app = Flask(__name__)


if __name__ == '__main__':
    for r in resources:
        add_resource(app, r)

    app.run(debug=True)
