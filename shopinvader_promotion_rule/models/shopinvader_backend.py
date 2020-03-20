# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.addons.queue_job.job import job


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    @api.multi
    @job(default_channel="root.shopinvader")
    def _job_sale_price_update(self, sales):
        """
        Inherit to re-compute also promotions rules
        :param sales: sale.order recordset
        :return:None
        """
        result = super(ShopinvaderBackend, self)._job_sale_price_update(sales)
        # This function is called now because this module depends on
        # shopinvader_promotion_rule. But maybe it should be extracted into
        # a new module.
        sales.apply_promotions()
        return result
