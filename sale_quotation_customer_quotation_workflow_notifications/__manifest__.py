# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Odoo/addons/Sale Quotation Customer Quotation Workflow Notifications",
    "summary": """Custom notifications handeling for "customer quotation" workflow on sale orders""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        # Third-party
        "sale_quotation",
    ],
    "data": ["data/mail_message_subtype.xml"],
    "assets": {
        "web.assets_backend": [
            "sale_quotation_customer_quotation_workflow_notifications/static/src/components/follower_subtype_list/follower_subtype_list.js",
            "sale_quotation_customer_quotation_workflow_notifications/static/src/components/follower_subtype_list/follower_subtype_list.xml",
        ],
    },
    "demo": [],
}
