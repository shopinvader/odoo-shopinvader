# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _is_item(self, line):
        return super()._is_item(line) and not line.is_reward_line

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res.update(
            {
                "promo_code": sale.promo_code,
                "reward_amount": sale.reward_amount,
                "applied_coupon_ids": self._convert_coupon(sale.applied_coupon_ids),
                "generated_coupon_ids": self._convert_coupon(sale.generated_coupon_ids),
                "no_code_promo_program_ids": self._convert_coupon_programs(
                    sale.no_code_promo_program_ids
                ),
                "code_promo_program_id": (
                    sale.code_promo_program_id.jsonify(
                        self._parser_coupon_program(), one=True
                    )
                    if sale.code_promo_program_id
                    else False
                ),
            }
        )
        return res

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res.update(
            {
                "is_reward_line": line.is_reward_line,
            }
        )
        return res

    def _parser_coupon(self):
        return [
            "id",
            "code",
            "state",
            "expiration_date",
            ("partner_id:partner", self._parser_coupon_partner()),
            ("program_id:program", self._parser_coupon_program()),
        ]

    def _parser_coupon_partner(self):
        return ["id", "name"]

    def _parser_coupon_program(self):
        return ["id", "name"]

    def _convert_coupon(self, coupons):
        return {
            "items": coupons.jsonify(self._parser_coupon()),
            "count": len(coupons),
        }

    def _convert_coupon_programs(self, programs):
        return {
            "items": programs.jsonify(self._parser_coupon_program()),
            "count": len(programs),
        }
