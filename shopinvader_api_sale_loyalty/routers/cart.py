# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction

from ..schemas import LoyaltyCardInput, LoyaltyRewardInput, Sale


@cart_router.post("/apply_coupon/{uuid}", deprecated=True)
@cart_router.post("/apply_coupon", deprecated=True)
@cart_router.post("/{uuid}/coupon")
@cart_router.post("/current/coupon")
@cart_router.post("/coupon")
def apply_coupon(
    data: LoyaltyCardInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale | None:
    """
    Apply a coupon on a specific cart.

    One can specify in LoyaltyCartInput which reward to choose, and
    which free product to choose.
    If some info is missing to uniquely determine which reward to apply,
    raise an error.
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if cart:
        env["shopinvader_api_cart.cart_router.helper"]._apply_coupon(cart, data)
    return Sale.from_sale_order(cart) if cart else None


@cart_router.post("/apply_reward/{uuid}", deprecated=True)
@cart_router.post("/apply_reward", deprecated=True)
@cart_router.post("/{uuid}/reward")
@cart_router.post("/current/reward")
@cart_router.post("/reward")
def apply_reward(
    data: LoyaltyRewardInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale | None:
    """
    Apply claimable rewards on a specific cart.

    One can specify in LoyaltyReardInput which free product to choose.
    If this piece of info is needed and missing, raise an error.
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if cart:
        env["shopinvader_api_cart.cart_router.helper"]._apply_reward(cart, data)
    return Sale.from_sale_order(cart) if cart else None


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    # Apply coupon
    @api.model
    def _check_code_and_reward(self, cart, code, reward_id=None):
        """
        * Check the code is valid.
        * Check the provided reward is allowed.
          If no reward is given, return the unique allowed reward,
          or raise an error.

          :return: the browsed reward
        """
        status = cart._try_apply_code(code)
        if "error" in status:
            raise UserError(status["error"])
        all_rewards = self.env["loyalty.reward"]
        for rewards in status.values():
            all_rewards |= rewards

        if not all_rewards:
            raise UserError(_("No reward available for this code."))
        if reward_id and reward_id not in all_rewards.ids:
            raise UserError(_("Reward not allowed for this code."))
        if not reward_id and len(all_rewards) > 1:
            raise UserError(_("Several rewards available. Please specify one."))

        if reward_id:
            return self.env["loyalty.reward"].browse(reward_id)
        return all_rewards[0]  # In this case only 1 reward available

    @api.model
    def _check_free_reward_product(self, reward, product_id=None):
        """
        Check the free product is allowed (if given) or check
        that it is unique (if not given).

        :return: the free product id
        """
        if not reward.reward_type == "product":
            return

        reward_products = reward.reward_product_ids

        if not reward_products:
            raise UserError(_("No free products available."))
        if product_id and product_id not in reward_products.ids:
            raise UserError(_("Free product not allowed for this reward."))
        if not product_id and len(reward_products) > 1:
            raise UserError(_("Several free products available. Please specify one."))

        if product_id:
            return product_id
        return reward_products[0].id

    @api.model
    def _apply_coupon(self, cart: "SaleOrder", data: LoyaltyCardInput):
        """Apply a coupon or promotion code.

        It can raise UserError if coupon is not applicable, or
        if the coupon let the choice between several rewards, and the
        selected reward is not specified.
        """
        reward = self._check_code_and_reward(cart, data.code, data.reward_id)
        product_id = None
        if reward.reward_type == "product":
            product_id = self._check_free_reward_product(reward, data.free_product_id)

        self.env["sale.loyalty.reward.wizard"].sudo().create(
            {
                "order_id": cart.id,
                "selected_reward_id": reward.id if reward else None,
                "selected_product_id": product_id if product_id else None,
            }
        ).action_apply()
        return cart

    # Apply claimable reward
    def _apply_reward(self, cart: "SaleOrder", data: LoyaltyRewardInput):
        """
        Try to apply the given reward.

        Raise an error if there is a choice between free products
        and the chosen product is not specified.
        """
        cart._update_programs_and_rewards()
        reward = self.env["loyalty.reward"].browse(data.reward_id)
        product_id = self._check_free_reward_product(reward, data.free_product_id)
        return (
            self.env["sale.loyalty.reward.wizard"]
            .sudo()
            .create(
                {
                    "order_id": cart.id,
                    "selected_reward_id": data.reward_id,
                    "selected_product_id": product_id if product_id else None,
                }
            )
            .action_apply()
        )

    # Apply automatic rewards at cart updates
    def _apply_automatic_rewards(self, cart: SaleOrder):
        claimable_rewards = cart._get_claimable_rewards()

        for coupon, rewards in claimable_rewards.items():
            if (
                len(rewards) > 1
                or len(coupon.program_id.reward_ids) != 1
                or (rewards.reward_type == "product" and rewards.multi_product)
                or rewards.id in cart.order_line.mapped("reward_id").ids
            ):
                continue
            try:
                cart._apply_program_reward(rewards, coupon)
            except UserError:  # pylint: disable=except-pass
                pass

    @api.model
    def _sync_cart(
        self,
        partner: ResPartner,
        cart: SaleOrder,
        uuid: str,
        transactions: list[CartTransaction],
    ):
        cart = super()._sync_cart(partner, cart, uuid, transactions)
        # Try to auto apply rewards.
        # Only rewards that are the only reward of the program and not
        # with a multi product reward
        if cart:
            cart._update_programs_and_rewards()
            self._apply_automatic_rewards(cart)
        return cart
