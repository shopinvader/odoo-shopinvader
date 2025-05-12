# Copyright 2018 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Quotation State",
    "summary": "Sale Quotation State",
    "version": "16.0.0.1.0",
    "category": "e-commerce",
    "development_status": "Production/Stable",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": ["sale_cart"],
    "data": [
        "views/sale_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
