# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.osv import expression


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    def _job_sale_price_update(self, sales):
        """
        Jobify the process to update prices.
        After launching the price update, we also have to re-apply promotions
        (in case of the promotion change and conditions doesn't match anymore).
        Could be inherited to add others prices recompute.
        :param sales: sale.order recordset
        :return: None
        """
        sales._update_pricelist_and_update_line_prices()

    def _job_split_sale_price_update(self, sales):
        """
        Split the current job on many SO to 1 job per SO.
        To avoid rollback full price update in case of error.
        Better to have 1 SO bad recomputed instead of all SO.
        :param sales: sale.order recordset
        :return: bool
        """
        for sale in sales:
            description = "Recompute prices for cart %s" % sale.display_name
            self.with_delay(description=description)._job_sale_price_update(
                sale
            )
        return True

    def launch_sale_price_update(self):
        domain = expression.normalize_domain(
            [("shopinvader_backend_id", "in", self.ids)]
        )
        return self.cron_launch_sale_price_update(domain)

    @api.model
    def cron_launch_sale_price_update(self, domain=False):
        """
        Retrieve cart to update then apply the recalculation
        (could be used for a cron)
        :param domain: list/domain
        :return: bool
        """
        domain = domain or []
        sale_domain = expression.normalize_domain(
            [("typology", "=", "cart"), ("state", "=", "draft")]
        )
        domain = expression.AND([domain, sale_domain])
        sale_carts = self.env["sale.order"].search(domain)
        if sale_carts:
            description = "Recompute prices for carts (split: 1 job per cart)"
            return self.with_delay(
                description=description
            )._job_split_sale_price_update(sale_carts)
