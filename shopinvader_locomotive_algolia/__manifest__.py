# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Locomotive algolia",
    "summary": """
        This addons is used to push the initial algolia configuration
        to locomotive""",
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptcamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["component", "shopinvader_locomotive", "shopinvader_algolia"],
    "data": ["views/se_backend_algolia.xml"],
}
