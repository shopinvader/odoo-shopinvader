# Copyright 2020 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Rollback partner type to default `contact`
    cr.execute(
        "UPDATE res_partner SET type = 'contact' WHERE type = 'invalid_client_user'"
    )
    _logger.info(
        "Replace res_partner.type = 'invalid_client_user' w/ 'contact'"
    )
