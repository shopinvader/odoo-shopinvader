# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Address",
    "summary": "Adds a service to manage shopinvader invoicing and delivery address",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_router_helper",
        "shopinvader_schema_address",
        "extendable_fastapi",
    ],
    "data": [
        "security/res_groups.xml",
        "security/res_partner.xml",
    ],
    "installable": True,
}
