# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader App Demo",
    "summary": """
        Adds a demo application on fastapi endpoint for a
        demo shopinvader application that takes every router
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "shopinvader_api_address",
        "shopinvader_api_cart",
        "shopinvader_anonymous_partner",
        "shopinvader_fastapi_auth_jwt",
    ],
    "external_dependencies": {"python": ["fastapi"]},
    "data": [
        "views/fastapi_endpoint.xml",
    ],
    "demo": [
        "demo/res_users.xml",
        "demo/res_groups.xml",
        "demo/fastapi_endpoint.xml",
    ],
}
