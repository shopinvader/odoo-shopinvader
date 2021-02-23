# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Notification default",
    "summary": """
        Provide default notification templates for Shopinvader suite.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "email_template_qweb"],
    "data": [
        "templates/layout.xml",
        "templates/cart_email.xml",
        "templates/sale_email.xml",
        "templates/invoice_email.xml",
        "templates/customer_profile_email.xml",
        "templates/customer_address_email.xml",
        "data/email_template.xml",
        "data/shopinvader_notification.xml",
    ],
}
