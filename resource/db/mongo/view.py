#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson import ObjectId
from jsonpatch import JsonPatch

from resource import View, Response, status
from resource.core.exceptions import NotFound
from resource.utils import get_exception_detail


class Collection(View):
    """For MongoDB (NoSQL)."""

    def get_doc(self, pk):
        doc = self.engine.find_one({'_id': ObjectId(pk)})
        if doc:
            return doc
        else:
            raise NotFound()

    def get(self, pk=None, filter_=None):
        if pk is None:
            filter_ = filter_ or {}
            return Response(list(self.engine.find(filter_)))
        else:
            return Response(self.get_doc(pk))

    def post(self, data):
        form = self.form_cls(data)
        if form.is_valid():
            self.engine.insert(form.document)
            return Response(status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, pk, data):
        form = self.form_cls(data)
        if form.is_valid():
            doc = form.document
            doc.update({'_id': ObjectId(pk)})
            self.engine.remove({'_id': doc['_id']})
            self.engine.insert(doc)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, pk, data):
        doc = self.get_doc(pk)

        # do JSON-Patch
        patch_data = JsonPatch(data)
        try:
            patch_data.apply(doc, in_place=True)
        except Exception as e:
            return Response({'jsonpatch_error': get_exception_detail(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        # validate data after JSON-Patch
        form = self.form_cls(doc)
        if form.is_valid():
            self.engine.save(form.document)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        doc = self.get_doc(pk)
        self.engine.remove({'_id': doc['_id']})
        return Response(status=status.HTTP_204_NO_CONTENT)
