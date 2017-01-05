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
import StringIO
import base64


class LocomotiveApiError(Exception):

    def __init__(self, response, status_code):
        message = response.pop('error')
        super(LocomotiveApiError, self).__init__(message)
        self.status_code = status_code
        self.extra = response


class LocomotiveResource(object):

    def __init__(self, client):
        self.client = client
        self.call = self.client.call
        self.path = None

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


class LocomotiveContent(LocomotiveResource):

    def __init__(self, client, content_type):
        super(LocomotiveContent, self).__init__(client)
        self.path = '/content_types/%s/entries' % content_type


class LocomotiveAsset(LocomotiveResource):

    def __init__(self, client):
        super(LocomotiveAsset, self).__init__(client)
        self.path = '/content_assets'

    # TODO FIXME miss the key 'content_asset'
    def write(self, id_or_slug, data):
        f = StringIO.StringIO()
        f.write(base64.b64decode(data['base64']))
        f.seek(0)
        return self.call('put', self._path_with_slug(id_or_slug),
            files={'source': (data['filename'], f)})

    # TODO FIXME miss the key 'content_asset'
    def create(self, data):
        f = StringIO.StringIO()
        f.write(base64.b64decode(data['base64']))
        f.seek(0)
        return self.call('post', self.path,
            files={'source': (data['filename'], f)})


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
            #'Content-Disposition': 'form-data',
            #'name': "content_asset[source]",
            }

    def call(self, method, url, data=None, files=None):
        kwargs = {'headers': self.header()}
        if method == 'get':
            kwargs['params'] = data
        else:
            kwargs['json'] = data
            kwargs['files'] = files
        res = getattr(requests, method)(self.url + url, **kwargs)
        if res.status_code/100 != 2:
            raise LocomotiveApiError(res.json(), res.status_code)
        return res.json()

    def content(self, content_type):
        return LocomotiveContent(self, content_type)

    def asset(self):
        return LocomotiveAsset(self)


#####


class LocomotiveAdapter(CRUDAdapter):

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
        return self.resource.create(vals)

    def write(self, external_id, vals):
        return self.resource.write(external_id, vals)

    def delete(self, binding_id):
        self.resource.delete(binding_id)


class LocomotiveContentAdapter(LocomotiveAdapter):
    _content_type = None

    def __init__(self, connector_env):
        super(LocomotiveContentAdapter, self).__init__(connector_env)
        self.resource = self.client.content(self._content_type)


class LocomotiveAssetAdapter(LocomotiveAdapter):

    def __init__(self, connector_env):
        super(LocomotiveAssetAdapter, self).__init__(connector_env)
        self.resource = self.client.asset()
