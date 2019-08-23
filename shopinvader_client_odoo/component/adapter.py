# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent, Component

import requests


class OdooAdapter(AbstractComponent):
    _name = "odoo.client.adapter"
    _inherit = "shopinvader.client.adapter"

    def __init__(self, work_context):
        super().__init__(work_context)

    def _get_api_key(self):
        return self.client_data['client_api_key']

    def _get_odoo_client_url(self):
        return self.client_data['location']

    def _make_url(self, endpoint):
        return '/'.join(
            [
                self._get_odoo_client_url().rstrip('/'),
                'shopinvader',
                endpoint.lstrip('/'),
            ]
        )

    def _make_request(self, method, endpoint, data=None) :
        url = self._make_url(endpoint)
        headers = {'API_KEY': self._get_api_key()}
        return requests.request(method, url, headers=headers, json=data or {})


class OdooBackendAdapter(Component):
    _name = "odoo.backend.adapter"
    _inherit = [
        "shopinvader.backend.client.adapter",
        "odoo.client.adapter",
    ]

    def write(self, external_id, vals):
        print(vals)
        return self._make_request('POST', 'settings/update', vals)

    def read(self, external_id):
        vals = self._make_request('GET', 'settings')
        print(vals)
        return vals
