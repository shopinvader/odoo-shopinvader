# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from ..backend import locomotivecms
import logging
_logger = logging.getLogger(__name__)


#### TODO create a python lib for that code
import requests
import json


class LocomotiveApiError(Exception):

    def __init__(self, response, status_code):
        message = response.pop('error')
        super(LocomotiveApiError, self).__init__(message)
        self.status_code = status_code
        self.extra = response


class LocomotiveContent(object):

    def __init__(self, client, content_type):
        self.client = client
        self.content_type = content_type
        self.path = '/content_types/%s/entries' % content_type
        self.call = self.client.call

    def _path_with_slug(self, id_or_slug):
        return self.path + '/' + id_or_slug

    def index(self):
        # TODO add filter
        return self.call('get', self.path)

    def read(self, id_or_slug):
        return self.call('get', self._path_with_slug(id_or_slug))

    def write(self, id_or_slug, data):
        return self.call(
            'put',
            self._path_with_slug(id_or_slug),
            data={'content_entry': data})

    def create(self, data):
        return self.call('post', self.path, data={'content_entry': data})

    def add(self, data):
        print data
        return self.update(data['odoo_id'], data=data)


class LocomotiveClient(object):

    def __init__(self, email, api_key, handle, url):
        self.api_key = api_key
        self.email = email
        self.handle = handle
        self.url = url + '/locomotive/api/v3'

    def auth(self):
        # TODO catch error
        r = requests.post(
            self.url + '/tokens.json', {
                'api_key': self.api_key,
                'email': self.email,
                })
        self.token = r.json()['token']

    def header(self):
        return {
            'X-Locomotive-Account-Email': self.email,
            'X-Locomotive-Account-Token': self.token,
            'X-Locomotive-Site-Handle': self.handle,
            }

    def call(self, method, url, data=None):
        kwargs = {'headers': self.header()}
        if method == 'get':
            kwargs['params'] = data
        else:
            kwargs['json'] = data
        res = getattr(requests, method)(self.url + url, json=data, headers=self.header())
        if res.status_code/100 != 2:
            raise LocomotiveApiError(res.json(), res.status_code)
        return res.json()

    def content(self, content_type):
        return LocomotiveContent(self, content_type)

#####



class LocomotivecmsAdapter(CRUDAdapter):
    _model_name = None

    __pool = {}  # pool of connection

    def __init__(self, connector_env):
        backend = connector_env.backend_record
        client = LocomotiveClient(
             backend.username,
             backend.password,
            'adaptoo',
             #backend.handle,
             backend.location)
        client.auth()
        self.client = client

    def create(self, vals):
        res = self.client.content('products').create(vals)
        return res['_id']

    def write(self, external_id, vals):
        res = self.client.content('products').write(external_id, vals)
        return res['_id']

    def delete(self, binding_id):
        self.client.content('products').delete(binding_id)
