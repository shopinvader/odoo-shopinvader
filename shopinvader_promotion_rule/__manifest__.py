# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Shopvinvader Promotion Rule",
    "summary": "Module to manage Promotion Rule with shopinvader",
    "version": "10.0.1.3.0",
    "category": "Sale",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion, " "ACSONE SA / NV",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["shopinvader", "component", "sale_promotion_rule"],
    "data": ["views/sale_promotion_rule.xml"],
}
