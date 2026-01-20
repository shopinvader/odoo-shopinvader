# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Lead",
    "summary": """
        Lead FastAPI adding a service for creating CRM leads.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "crm",
        "extendable_fastapi",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_crm_lead.xml",
    ],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable-pydantic>=1.2.0",
        ],
    'installable': False,
},
    'installable': False,
}
