# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Security Base",
    "summary": "Read access on currency, uom, country, lang...",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": [
        "fastapi",
        "uom",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_res_country.xml",
        "security/acl_res_currency.xml",
        "security/acl_res_lang.xml",
        "security/acl_res_partner_title.xml",
        "security/acl_uom_uom.xml",
    ],
    "installable": True,
}
