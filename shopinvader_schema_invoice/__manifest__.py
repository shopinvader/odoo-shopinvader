# Copyright 2023 Camptocamp SA (https://www.Camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader schema invoice",
    "summary": "Add schema for invoices",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Camptocamp",
    "license": "AGPL-3",
    "depends": [
        "fastapi",
        "pydantic",
        "extendable",
        "account",
    ],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.2.0", "pydantic>=2.0.0"]
    },
}
