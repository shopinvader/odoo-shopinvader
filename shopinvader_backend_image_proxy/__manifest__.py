# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader backend image proxy",
    "summary": (
        "Add possibility to replace the image URL "
        "by the proxy url set on the SE backend"
    ),
    "version": "14.0.1.0.2",
    "category": "e-commerce",
    "author": "Akretion,ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "depends": ["shopinvader_image"],
    "data": ["views/shopinvader_backend.xml"],
    "installable": True,
}
