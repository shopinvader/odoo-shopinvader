This module is designed to be extended, so you can add your own options to the cart
lines.

In order to do so, you need to extend the `SaleLineOptions` schema and add your own
options:

```python
class SaleLineOptions(BaseSaleLineOptions, extends=True):
    engraving: str | None = None
    special: bool = False

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        rv = super().from_sale_order_line(odoo_rec)
        rv.engraving = odoo_rec.carving or None
        rv.special = odoo_rec.special
        return rv
```

Then you will need to extend the `SaleOrderLine` model to add support for you options in
the cart line matching and in the cart line transfer:

```python
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    carving = fields.Char()
    special = fields.Boolean()

    def _match_cart_line(
        self,
        product_id,
        carving=None,
        special=None,
        **kwargs,
    ):
        rv = super()._match_cart_line(
            product_id,
            carving=carving,
            special=special,
            **kwargs,
        )
        return rv and self.carving == carving and self.special == special

    def _prepare_cart_line_transfer_values(self):
        vals = super()._prepare_cart_line_transfer_values()
        vals["carving"] = self.carving
        vals["special"] = self.special
        return vals
```

And finally, you will need to extend the `ShopinvaderApiCartRouterHelper` to add support
for your options in the cart line creation from the transaction API:

```python
class ShopinvaderApiCartRouterHelper(
    models.AbstractModel
):  # pylint: disable=consider-merging-classes-inherited
    _inherit = "shopinvader_api_cart.cart_router.helper"

    @api.model
    def _apply_transactions_creating_new_cart_line_prepare_vals(
        self, cart: SaleOrder, transactions: list[CartTransaction], values: dict
    ):
        options = transactions[0].options
        if options:
            values["carving"] = options.engraving
            values["special"] = options.special

        return values
```
