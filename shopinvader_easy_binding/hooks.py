# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Automatically set company shopinvader backend

    For companies having only 1 shopinvader.backend, automatically
    set it as its main backend.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    groups = env["shopinvader.backend"].read_group(
        domain=[],
        fields=["company_id"],
        groupby=["company_id"],
        lazy=False,
    )
    single_backend_company_ids = [
        d["company_id"][0] for d in groups if d["__count"] == 1
    ]
    if single_backend_company_ids:
        backends = env["shopinvader.backend"].search(
            [("company_id", "in", single_backend_company_ids)]
        )
        for backend in backends:
            backend.company_id.shopinvader_company_backend_id = backend
