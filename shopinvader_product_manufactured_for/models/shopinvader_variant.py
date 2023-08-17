# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from psycopg2.extensions import AsIs

from odoo import models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    manufactured_for_partners = Serialized(compute="_compute_manufactured_for_partners")

    def _compute_manufactured_for_partners(self):
        pids = self.mapped("record_id").ids
        # Use raw sql because accessing the m2m can be very slow
        query = """
            SELECT
                product_id,ARRAY_AGG(partner_id)
            FROM
                %s
            WHERE
                product_id in %s
            GROUP BY
                product_id
        """
        prod_model = self.env["product.product"]
        rel_table = prod_model._fields["manufactured_for_partner_ids"].relation
        self.env.cr.execute(query, (AsIs(rel_table), tuple(pids)))
        mapping = dict(self.env.cr.fetchall())
        for record in self:
            # No value hack to make Algolia search via facets work properly.
            # We must lookup products that have this field valued or empty.
            # On algolia you cannot filter by given value and EMPTY value
            # at the same time. Hence, we set a default value for no value.
            record.manufactured_for_partners = mapping.get(
                record.record_id.id, ["_NOVALUE_"]
            )

    def _redirect_existing_url(self):
        # Avoid redirection of product manufactured for specific partners.
        # Such products are not public thus is useless to redirect their URLs
        # to the parent category to preserve SEO links.
        # Moreover, this makes the index record size grow
        # which is not nice (especially w/ Algolia that has a limited size).
        to_not_redirect = self.filtered(lambda x: x.manufactured_for_partner_ids)
        return super(
            ShopinvaderVariant, self - to_not_redirect
        )._redirect_existing_url()
