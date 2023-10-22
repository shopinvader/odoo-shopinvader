# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Carrier",
    "summary": "Carrier integration for Shopinvader",
    "version": "14.0.2.3.1",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "delivery",
        "queue_job",
        "shopinvader",
        "sale_shipping_info_helper",
        "delivery_carrier_info",
    ],
    # odoo_test_helper is needed for the tests
    "data": ["views/backend_view.xml", "data/cart_step.xml"],
    "demo": [
        "demo/backend_demo.xml",
        "demo/mail_template.xml",
        "demo/shopinvader_notification.xml",
    ],
    "qweb": [],
}
