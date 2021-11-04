# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from psycopg2.extensions import AsIs

from odoo import models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    manufactured_for_partners = Serialized(compute="_compute_manufactured_for_partners")

    def _compute_manufactured_for_partners(self):
        pids = self.mapped("product_tmpl_id").ids
        # Use raw sql because accessing the m2m can be very slow
        query = """
            SELECT
                product_template_id,ARRAY_AGG(res_partner_id)
            FROM
                %s
            WHERE
                product_template_id in %s
            GROUP BY
                product_template_id
        """
        rel_table = (
            self.env["product.template"]
            ._fields["manufactured_for_partner_ids"]
            .relation
        )
        self.env.cr.execute(query, (AsIs(rel_table), tuple(pids)))
        mapping = dict(self.env.cr.fetchall())
        for record in self:
            # No value hack to make Algolia search via facets work properly.
            # We must lookup products that have this field valued or empty.
            # On algolia you cannot filter by given value and EMPTY value
            # at the same time. Hence, we set a default value for no value.
            record.manufactured_for_partners = mapping.get(
                record.product_tmpl_id.id, ["_NOVALUE_"]
            )
