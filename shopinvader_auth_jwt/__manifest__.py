# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader JWT Authentication",
    "version": "14.0.1.0.1",
    "summary": "Find shopinvader backend and partner from JWT token",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "depends": [
        "shopinvader",
        "auth_jwt",
    ],
    "data": [
        "views/shopinvader_backend.xml",
    ],
    "demo": [],
}
