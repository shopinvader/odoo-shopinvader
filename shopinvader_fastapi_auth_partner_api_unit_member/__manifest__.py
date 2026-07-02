# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Fastapi Auth Partner Api Unit Member",
    "summary": "This module glues the shopinvader unit member management with "
    "the fastapi auth partner api adding an auth state on members and an invite "
    "route.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_api_unit_member",
        "shopinvader_fastapi_auth_partner",
    ],
    "data": [
        "data/email_data.xml",
        "views/auth_directory_view.xml",
    ],
    "auto_install": True,
    "installable": True,
}
