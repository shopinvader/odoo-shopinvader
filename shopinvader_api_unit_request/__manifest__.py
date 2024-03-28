# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Unit Request Api",
    "summary": "This module adds the possibility to make a request from a cart "
    "as a collaborator of a unit to be later reviewed, merged and converted into a "
    "sale order by a unit manager.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_api_unit_member",
        "shopinvader_api_cart",
        "shopinvader_api_sale",
    ],
    "data": [
        "views/sale_order_views.xml",
        "security/sale_management_security.xml",
    ],
    "installable": True,
}
