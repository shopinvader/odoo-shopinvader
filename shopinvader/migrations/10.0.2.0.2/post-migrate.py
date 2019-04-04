# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """existing urls should not be synced."""
    cr.execute("update shopinvader_product set is_urls_sync_required=false")
    cr.execute("update shopinvader_category set is_urls_sync_required=false")
