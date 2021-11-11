# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.component.core import Component


class CartsService(Component):
    """Shopinvader service to manage multiple carts."""

    _inherit = "shopinvader.abstract.sale.service"
    _name = "shopinvader.carts.service"
    _usage = "carts"
    _expose_model = "sale.order"
    _description = __doc__

    # The following methods are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    def search(self, **params):
        """Gets every saved cart related to logged user
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def get(self, _id):
        """Gets info about given cart id.
        :param _id: int
        :return: dict/json
        """
        cart = self._get(_id)
        return {"data": self._to_json(cart)[0]}

    def select(self, _id):
        """Selects the cart with the given id.

        If there's already an active cart, it will be saved.

        :param _id: int
        :return: dict/json
        """
        # First, save the current cart (if any)
        self.component("cart").save()
        # Then, select the new one
        cart = self._get(_id)
        self._restore(cart)
        return self.component("cart")._to_json(cart)

    def delete(self, _id):
        """Deletes the cart with the given id.
        :param _id: int
        """
        cart = self._get(_id)
        cart.unlink()
        return {}

    # The following methods are 'private' and should be never NEVER be called
    # from the controller.
    # All params are trusted as they have been checked before

    def _restore(self, cart):
        cart.typology = "cart"

    def _get_sale_order_saved_cart_domain(self):
        return [
            ("typology", "=", "saved"),
            ("state", "=", "draft"),
        ]

    def _get_base_search_domain(self):
        """Domain used to retrieve user's carts.

        This domain MUST TAKE CARE of restricting the access to the carts visible
        for the current customer.

        :return: Odoo domain
        """
        # The partner must be set and not be the anonymous one
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return expression.normalize_domain(
            expression.AND(
                [
                    self._default_domain_for_partner_records(),
                    self._get_sale_order_saved_cart_domain(),
                ]
            )
        )

    # Validators

    def _validator_search(self):
        res = self._default_validator_search()
        res.pop("domain", None)
        return res

    def _validator_get(self):
        return {}

    def _validator_select(self):
        return {}

    def _validator_delete(self):
        return {}
