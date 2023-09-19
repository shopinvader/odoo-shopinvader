from odoo import fields

from odoo.addons.component.core import Component


class CustomerService(Component):
    """Shopinvader service to create and edit customers."""

    _inherit = "shopinvader.customer.service"

    def _parser_coupon(self):
        return [
            "id",
            "code",
            "expiration_date",
            (
                "program_id:program",
                [
                    "id",
                    "name",
                    "program_type",
                    ("reward_ids:rewards", self._parser_coupon_reward()),
                ],
            ),
        ]

    def _parser_coupon_reward(self):
        return [
            "id",
            "reward_type",
            "discount",
            "discount_mode",
            "discount_applicability",
            ("all_discount_product_ids:discount_products", self._parser_product()),
            ("reward_product_id:reward_product", self._parser_product()),
        ]

    def _parser_product(self):
        return [
            "id",
            "name",
        ]

    def _add_coupon_info(self, partner, info):
        coupons = (
            self.env["loyalty.card"]
            .search(
                [
                    ("partner_id", "=", partner.id),
                ]
            )
            .filtered(
                lambda coupon: (
                    not coupon.expiration_date
                    or coupon.expiration_date >= fields.Date.context_today(partner)
                )
                and (
                    not coupon.program_id.date_to
                    or coupon.program_id.date_to >= fields.Date.context_today(partner)
                )
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
