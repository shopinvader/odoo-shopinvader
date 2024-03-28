# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Schema Address",
    "summary": """
        Adds shchema address: address invoicing_address delivery_address""",
    "version": "16.0.1.3.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "pydantic",
        "extendable",
        "shopinvader_address",
    ],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.2.0", "pydantic>=2.0.0"]
    },
    "data": [],
    "demo": [],
    "installable": True,
}
