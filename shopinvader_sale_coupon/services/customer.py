from odoo import fields

from odoo.addons.component.core import Component


class CustomerService(Component):
    """Shopinvader service to create and edit customers."""

    _inherit = "shopinvader.customer.service"

    def _parser_coupon(self):
        return [
            "id",
            "code",
            "state",
            "expiration_date",
            (
                "program_id:program",
                [
                    "id",
                    "name",
                    "reward_type",
                    "reward_product_id",
                    "reward_product_quantity",
                    "discount_type",
                    "discount_percentage",
                    "discount_fixed_amount",
                ],
            ),
        ]

    def _add_coupon_info(self, partner, info):
        coupons = (
            self.env["coupon.coupon"]
            .search(
                [
                    ("partner_id", "=", partner.id),
                    ("state", "in", ("new", "sent")),
                ]
            )
            .filtered(
                lambda coupon: not coupon.expiration_date
                or coupon.expiration_date >= fields.Date.context_today(partner)
            )
        )
        if coupons:
            info["valid_coupons_ids"] = {
                "items": coupons.jsonify(self._parser_coupon()),
                "count": len(coupons),
            }
        return info

    def _to_customer_info(self, partner):
        info = super()._to_customer_info(partner)
        self._add_coupon_info(partner, info)
        return info
