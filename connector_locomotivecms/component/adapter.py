# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8106


from odoo.addons.component.core import AbstractComponent, Component

import logging
_logger = logging.getLogger(__name__)

try:
    import locomotivecms
except (ImportError, IOError) as err:
    _logger.debug(err)


_logger = logging.getLogger(__name__)


class LocomotiveAdapter(AbstractComponent):
    _name = 'locomotive.abstract.adapter'
    _inherit = ['base.backend.adapter', 'base.locomotive.connector']

    def __init__(self, work_context):
        super(LocomotiveAdapter, self).__init__(work_context)
        backend = self.collection
        self.client = locomotivecms.LocomotiveClient(
            backend.username,
            backend.password,
            backend.handle,
            backend.location)

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
