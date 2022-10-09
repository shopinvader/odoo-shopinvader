# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Locomotive Password Management",
    "summary": "Synchronize password to Locomotive users record.",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["shopinvader_locomotive"],
    "data": ["security/groups.xml", "views/shopinvader_partner_view.xml"],
}
