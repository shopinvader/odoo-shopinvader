# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models

# from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    typology = fields.Selection(
        selection_add=[("quotation", "Quotation")],
        ondelete={"quotation": "cascade"},
    )
