# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    def _redirect_existing_url(self):
        # Avoid redirection of product manufactured for specific partners.
        # Such products are not public thus is useless to redirect their URLs
        # to the parent category to preserve SEO links.
        # Moreover, this makes the index record size grow
        # which is not nice (especially w/ Algolia that has a limited size).
        to_not_redirect = self.filtered(lambda x: x.manufactured_for_partner_ids)
        return super(
            ShopinvaderProduct, self - to_not_redirect
        )._redirect_existing_url()
