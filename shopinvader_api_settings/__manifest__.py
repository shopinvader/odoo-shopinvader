# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Settings Api",
    "summary": "Adds a service to get commont settings",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_router_helper",
        "extendable",
        "extendable_fastapi",
        "fastapi",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "fastapi",
            "extendable_pydantic>=1.0.0",
            "pydantic>=2.0.0",
        ]
    },
    "installable": True,
}
