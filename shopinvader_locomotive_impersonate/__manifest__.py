# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Locomotive Impersonate",
    "summary": "Allow to log with any shopinvader partner directly from odoo",
    "version": "14.0.1.0.1",
    "development_status": "Alpha",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader_locomotive",
    ],
    "data": [
        "security/res_groups.xml",
        "views/shopinvader_partner_view.xml",
        "views/res_partner_view.xml",
    ],
    "demo": [],
}
