#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from flask import Flask

from rsrc import Resource
from rsrc.contrib.root import Root
from rsrc.contrib.db.mongo import Collection, serializer
from rsrc.contrib.dufilter import DuFilter
from rsrc.framework.flask import add_resource, make_root


DB = MongoClient().test


resources = [
    Resource('users', Collection, serializer=serializer,
             filter_cls=DuFilter,
             kwargs={'db': DB, 'table_name': 'user'})
]


app = Flask(__name__)


if __name__ == '__main__':
    for r in resources:
        add_resource(app, r)

    root = Resource('root', Root, uri='/',
                    kwargs={'resources': resources})
    make_root(app, root)

    app.run(debug=True)
