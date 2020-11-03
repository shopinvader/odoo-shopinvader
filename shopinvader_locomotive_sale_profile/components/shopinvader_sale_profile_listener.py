# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopinvaderRecordListener(Component):

    _inherit = "shopinvader.record.event.listener"

    _apply_on = ["res.partner"]

    def _get_fields_to_export(self):
        # Extend trigger fields to update partner role
        # TODO: As this is not perfect - it does not trigger when
        # shopinvader.partner model or backend is modified
        return super()._get_fields_to_export() + [
            "vat",
            "property_product_pricelist",
            "country_id",
        ]
