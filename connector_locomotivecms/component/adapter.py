# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import AbstractComponent, Component
import logging
import requests

_logger = logging.getLogger(__name__)


# TODO create a python lib for that code


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

    def search(self, page=1, per_page=80):
        return self.call(
            'get', self.path, {'page': page, 'per_page': per_page})

    def read(self, id_or_slug):
        return self.call('get', self._path_with_slug(id_or_slug))

    def write(self, id_or_slug, data):
        return self.call(
            'put',
            self._path_with_slug(id_or_slug),
            data={'content_entry': data})

    def create(self, data):
        return self.call('post', self.path, data={'content_entry': data})

    def delete(self, id_or_slug):
        return self.call('delete', self._path_with_slug(id_or_slug))


class LocomotiveContent(LocomotiveResource):

    def __init__(self, client, content_type):
        super(LocomotiveContent, self).__init__(client)
        self.path = '/content_types/%s/entries' % content_type


class LocomotiveAsset(LocomotiveResource):

    def __init__(self, client):
        super(LocomotiveAsset, self).__init__(client)
        self.path = '/content_assets'

    def write(self, id_or_slug, data):
        return self.call(
            'put', self._path_with_slug(id_or_slug),
            files={'source': (data['filename'], data['file'])})

    def create(self, data):
        return self.call(
            'post', self.path,
            files={'content_asset[source]': (data['filename'], data['file'])})


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

# end of lib code


class LocomotiveAdapter(AbstractComponent):
    _name = 'locomotive.abstract.adapter'
    _inherit = ['base.backend.adapter', 'base.locomotive.connector']

    def __init__(self, work_context):
        super(LocomotiveAdapter, self).__init__(work_context)
        backend = self.collection
        client = LocomotiveClient(
            backend.username,
            backend.password,
            backend.handle,
            backend.location)
        client.auth()
        self.client = client

    def create(self, vals):
        return self.resource.create(vals)

    def write(self, external_id, vals):
        return self.resource.write(external_id, vals)

    def delete(self, binding_id):
        self.resource.delete(binding_id)

    def read(self, external_id):
        return self.resource.read(external_id)

    def search(self, page=1, per_page=80):
        return self.resource.search(page=page, per_page=per_page)


class LocomotiveContentAdapter(Component):
    _name = 'locomotive.content.adapter'
    _inherit = 'locomotive.abstract.adapter'
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super(LocomotiveContentAdapter, self).__init__(work_context)
        self.resource = self.client.content(self._content_type)


class LocomotiveAssetAdapter(Component):
    _name = 'locomotive.asset.adapter'
    _inherit = 'locomotive.abstract.adapter'
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super(LocomotiveAssetAdapter, self).__init__(work_context)
        self.resource = self.client.asset()
