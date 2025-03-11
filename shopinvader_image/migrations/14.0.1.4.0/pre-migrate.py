# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)


def update_shopinvader_tables(cr):
    _logger.info("Updating shopinvader_backend table ...")
    queries = [
        "ALTER TABLE shopinvader_backend "
        "ADD COLUMN IF NOT EXISTS image_data_empty_alt_name_allowed BOOLEAN",
    ]
    for query in queries:
        cr.execute(query)


def migrate(cr, version):
    update_shopinvader_tables(cr)
