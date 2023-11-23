import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    seller_backends = env["shopinvader.backend"].search([("seller_access", "=", True)])
    all_seller_cart_domain = [
        ("shopinvader_backend_id", "in", seller_backends.mapped("id")),
        ("typology", "=", "cart"),
        ("user_id", "!=", False),
    ]
    all_seller_carts = env["sale.order"].search(all_seller_cart_domain)
    _logger.info(
        "Marking %s carts as created by seller",
        len(all_seller_carts),
    )
    all_seller_carts.write({"created_by_seller": True})
