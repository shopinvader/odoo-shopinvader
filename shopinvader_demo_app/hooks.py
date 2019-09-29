# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def post_init_hook(cr, registry):
    """
    Fix some demo data to work with
    https://github.com/shopinvader/shopinvader-getting-started
    """
    openupgrade.load_xml(
        cr,
        "shopinvader_demo_app",
        "demo/se_backend_elasticsearch_demo.xml",
        mode="init",
    )
    openupgrade.load_xml(
        cr,
        "shopinvader_demo_app",
        "demo/storage_backend_demo.xml",
        mode="init",
    )
