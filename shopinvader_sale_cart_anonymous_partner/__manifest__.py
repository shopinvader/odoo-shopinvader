# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Sale Cart Anonymous Partner",
    "summary": "Glue module between shopinvader_sale_cart and "
    "shopinvader_anonymous_partner. This module solves cart conflicts "
    "when an anonymous user sign in.",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_sale_cart",
        "shopinvader_anonymous_partner",
    ],
    "auto_install": True,
}
