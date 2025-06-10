# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Cart Cancel",
    "summary": "Cancel cart via Fastapi",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "depends": [
        "extendable_fastapi",
        "shopinvader_api_cart",
    ],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable-pydantic>=1.2.0",
        ]
    },
}
