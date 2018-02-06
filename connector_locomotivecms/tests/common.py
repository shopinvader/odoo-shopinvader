# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from contextlib import contextmanager

import mock
from odoo.tests.common import TransactionCase


class AlgoliaIndexMock(object):
    """ Used to simulate the calls to Algolia
    For a call (request) to Algolia, returns a stored
    response.
    """

    def __init__(self):
        self._calls = []

    def add_objects(self, datas):
        self._calls.append(('add_objects', datas))
        return True

    def delete_objects(self, binding_ids):
        self._calls.append(('delete_objects', binding_ids))
        return True


class AlgoliaClientMock(object):

    def __init__(self):
        self.api = None
        self.secret = None
        self.index = {}

    def initIndex(self, name):
        self.index[name] = AlgoliaIndexMock()
        return self.index[name]


@contextmanager
def mock_api():
    algolia_mock = AlgoliaClientMock()

    def get_mock_interface(api, secret):
        algolia_mock.api = api
        algolia_mock.secret = secret
        return algolia_mock

    with mock.patch('algoliasearch.client.Client', get_mock_interface):
        yield algolia_mock


class SetUpAlgoliaBase(TransactionCase):

    def setUp(self):
        super(SetUpAlgoliaBase, self).setUp()
        self.backend = self.env.ref('connector_nosql_algolia.backend_1')
