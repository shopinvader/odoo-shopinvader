# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Shopinvader Schema Address',
    'summary': """
        Adds shchema address: address billing_address delivery_address""",
    'version': '16.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/shopinvader/odoo-shopinvader',
    "depends": [
        "pydantic",
        "extendable",
    ],
    "external_dependencies": {"python": ["extendable_pydantic", "pydantic"]},
    'data': [
    ],
    'demo': [
    ],
    "installable": True,
}
