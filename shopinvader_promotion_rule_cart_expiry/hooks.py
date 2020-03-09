# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Set default value for shopinvader_write_date on sale.order with write_date.
    """
    _logger.info(
        "Update every sale.order: set shopinvader_write_date with write_date."
    )
    query = """UPDATE sale_order SET shopinvader_write_date = write_date;"""
    cr.execute(query)
