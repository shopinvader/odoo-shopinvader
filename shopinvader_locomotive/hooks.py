# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def rename_module(cr):
    openupgrade.update_module_names(
        cr,
        [("connector_locomotivecms", "shopinvader_locomotive")],
        merge_modules=True,
    )
