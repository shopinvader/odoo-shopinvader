# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import AbstractComponent


class PartnerServiceMixin(AbstractComponent):
    _inherit = "shopinvader.partner.service.mixin"

    def _notify_partner_type_profile(self, partner, mode):
        notif = super()._notify_partner_type_profile(partner, mode)
        shop_partner = partner.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id == self.shopinvader_backend
        )
        if shop_partner.is_guest:
            notif = None
        return notif
