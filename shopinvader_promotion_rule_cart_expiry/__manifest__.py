# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Shopvinvader Promotion Rule cart expiry",
    "summary": "Module to fix incompatibility between shopinvader promotion rule "
    "and shopinvader cart expiry.",
    "version": "10.0.1.0.1",
    "category": "Sale",
    "website": "https://shopinvader.com",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["shopinvader_promotion_rule", "shopinvader_cart_expiry"],
    "post_init_hook": "post_init_hook",
}
