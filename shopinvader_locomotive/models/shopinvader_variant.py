# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    @api.multi
    def _unbind(self):
        """
        Inherit to call the delete on locomotive if the recordset is un-binded.
        :return: bool
        """
        result = super(ShopinvaderVariant, self)._unbind()
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                external_id = work.component(usage='binder').to_external(
                    record)
                if external_id:
                    record.with_delay().export_delete_record(
                        record.backend_id, external_id)
        return result

    @api.multi
    def _bind(self):
        """
        Inherit to re-bind the recordset.
        :return:
        """
        result = super(ShopinvaderVariant, self)._bind()
        for record in self:
            record.with_delay().export_record(_fields=record._fields.keys())
        return result
