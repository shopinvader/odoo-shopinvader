import logging

from odoo.upgrade.util.modules import rename_module

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Renaming 'sale_quotation' to 'sale_quotation_state'")
    rename_module(cr, "sale_quotation", "sale_quotation_state")
