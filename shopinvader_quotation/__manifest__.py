# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Quotation",
    "summary": "Shopinvader Quotation",
    "version": "14.0.2.3.1",
    "category": "e-commerce",
    "development_status": "Production/Stable",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": ["sale_quotation", "shopinvader"],
    "demo": ["demo/email_demo.xml", "demo/notification_demo.xml"],
    "data": [
        "data/ir_export_product.xml",
    ],
    "installable": False,
}
