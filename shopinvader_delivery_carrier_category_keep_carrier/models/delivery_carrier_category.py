# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrierCategory(models.Model):

    _inherit = "delivery.carrier.category"

    keep_carrier_on_shipping_change = fields.Boolean(copy=False)
