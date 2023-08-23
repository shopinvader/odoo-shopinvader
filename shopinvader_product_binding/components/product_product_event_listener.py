# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ProductProductEventListener(Component):
    _name = "product.product.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["product.product"]

    # fmt: off
    @skip_if(
        lambda self, record, **kwargs: not record.product_tmpl_id.
        shopinvader_bind_ids
    )
    # fmt: on
    def on_record_create(self, record, fields=None):
        """
        Event listener on the create of product.product.
        In case of the related product.template has been binded, we have to
        bind every new product.product (checked with the skip_if(...).
        By default, they shouldn't be binded (force active = False)
        :param record: product.template recordset
        :param fields: list of str
        :return:
        """
        shopinv_products = record.mapped("product_tmpl_id.shopinvader_bind_ids")
        shopinv_variants = self._launch_shopinvader_variant_creation(shopinv_products)
        # If at least 1 is True, force False
        if any(shopinv_variants.mapped("active")):
            shopinv_variants.write({"active": False})

    def _launch_shopinvader_variant_creation(self, shopinvader_products):
        """
        Launch the creation of the shopinvader.variant based on the (given)
        shopinvader.product
        :param shopinvader_products: shopinvader.product recordset
        :return: shopinvader.variant recordset
        """
        shopinv_variants = self.env["shopinvader.variant"].browse()
        for shopinv_product in shopinvader_products:
            shopinv_variants |= shopinv_product._create_shopinvader_variant()
        return shopinv_variants
