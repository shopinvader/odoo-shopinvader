# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    bind_new_customers = fields.Boolean(
        help="Check this if you want to automatically bind new customers "
        "to this backend."
    )
    new_customer_autobind_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="New Customer Auto Binding Email",
        help="Fill in this field with Mail Template that will be used to send a welcome mail to customers"
        "automatically bound to Shopinvader backends.",
    )
