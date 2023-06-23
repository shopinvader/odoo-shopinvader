BillingAddress
  In the context of shopinvader, the ``BillingAddress`` corresponds to the authenticated partner itself.
  Therefore, the ``Billing Address`` is unique for each partner.

  Creation of ``Billing Address`` is not supported since it corresponds to the authenticated partner.

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_billing_address(self, vals: dict, address_id: int) -> "ResPartner"

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*

ShippingAddress
  In the context of shopinvader, a ``ShippingAddress`` corresponds to any delivery address linked to the authenticated partner.
  A partner can have between 0 and n ``ShippingAddress``.

  It can be created using:

  .. code-block:: python

    def _create_shopinvader_shipping_address(self, vals: dict) -> "ResPartner":

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_shipping_address(self, vals: dict, address_id: int) -> "ResPartner":

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*
