# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Address",
    "summary": """
        Adds profile and address Fastapi""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "shopinvader_schema_address",
        "extendable_fastapi",
    ],
    "data": [
        "security/res_groups.xml",
        "security/res_partner.xml",
        "security/account_move.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["fastapi", "extendable_pydantic", "pydantic"]},
    "installable": True,
}
