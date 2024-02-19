# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Profile",
    "summary": """Sale profiles""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "e-commerce",
    "author": "Akretion,ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["account"],
    "data": ["security/groups.xml", "security/shopinvader_sale_profile.xml"],
    "demo": ["demo/account.xml", "demo/pricelist.xml"],
    "installable": True,
}
