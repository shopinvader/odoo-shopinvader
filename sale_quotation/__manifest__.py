# Copyright 2018 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Quotation",
    "summary": "Sale Quotation",
    "version": "18.0.1.0.0",
    "category": "e-commerce",
    "development_status": "Production/Stable",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": [
        "shopinvader_product_order_mode_on_request",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "installable": True,
}
