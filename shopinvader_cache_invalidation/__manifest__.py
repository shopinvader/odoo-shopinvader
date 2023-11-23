# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).

{
    "name": "Custom Shopinvader Cache Purge",
    "summary": "List url to purge and manage purge",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["shopinvader_search_engine"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/shopinvader_url_purge.xml",
        "views/shopinvader_backend.xml",
        "views/shopinvader_url_purge_type_view.xml",
    ],
    "demo": [],
}
