# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ShopinvaderBindingListener(Component):
    _inherit = "shopinvader.binding.event.listener"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        if record.is_guest:
            return
        return super(ShopinvaderBindingListener, self).on_record_create(
            record=record, fields=fields
        )

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if record.is_guest:
            return
        return super(ShopinvaderBindingListener, self).on_record_write(
            record=record, fields=fields
        )
