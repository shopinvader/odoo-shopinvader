# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "shopinvader sale channel",
    "summary": "Shopinvader Sale Channel",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader_api_cart",
        "sale_channel",
    ],
    "data": [
        "views/fastapi_endpoint_view.xml",
    ],
    "demo": [],
}
