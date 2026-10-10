# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Unit Member",
    "summary": "This module adds a service to shopinvader to manage units members: "
    "managers and collaborators.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "extendable",
        "extendable_fastapi",
        "fastapi",
        "shopinvader_unit_management",
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
