# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Address Api",
    "summary": """
        Adds a service to manage shopinvader billing and shipping address""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "extendable",
        "extendable_fastapi",
        "fastapi",
        "shopinvader_address",
        "shopinvader_schema_address",
    ],
    "data": [
        "security/res_groups.xml",
        "security/res_partner.xml",
    ],
    "external_dependencies": {
        "python": ["fastapi", "extendable_pydantic>=1.0.0", "pydantic>=2.0.0"]
    },
    "installable": True,
}
