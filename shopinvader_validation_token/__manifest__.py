# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader validation token",
    "summary": """Implements a security layer on the registration and/or
    customer mode. To ensure a customer doesn't use the email of somebody else,
    it generates a token/code send using notification and
    the customer has to fill it on the front-side.""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["shopinvader"],
    "data": [
        "data/ir_cron.xml",
        "data/mail_template.xml",
        "views/shopinvader_security_token.xml",
        "views/shopinvader_backend.xml",
        "security/shopinvader_security_token.xml",
    ],
}
