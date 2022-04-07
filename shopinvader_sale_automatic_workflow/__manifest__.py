# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Automatic Workflow",
    "summary": "Use sale automatic workflows for Shopinvader orders",
    "version": "14.0.1.0.1",
    "author": "Camptocamp SA",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Shopinvader",
    "depends": ["shopinvader", "sale_automatic_workflow"],
    "data": ["views/shopinvader_backend.xml"],
    "auto_install": True,
}
