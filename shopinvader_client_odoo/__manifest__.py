# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Base Client Connector",
    "version": "12.0.1.0.0",
    "category": "Connector",
    "summary": """
        Manage interaction between Shopinvader and the frontend client
    """,
    "author": "Camptocamp, Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": [
        "shopinvader_client_base",
    ],
    "data": ["views/shopinvader_backend_view.xml", ],
    "demo": ["demo/backend_demo.xml"],
    "installable": True,
}
