InvoicingAddress
  In the context of shopinvader, the ``InvoicingAddress`` corresponds to the authenticated partner itself.
  Therefore, the ``Invoicing Address`` is unique for each partner.

  Creation of ``Invoicing Address`` is not supported since it corresponds to the authenticated partner.

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_invoicing_address(self, vals: dict, address_id: int) -> "ResPartner"

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*

DeliveryAddress
  In the context of shopinvader, a ``DeliveryAddress`` corresponds to any delivery address linked to the authenticated partner.
  A partner can have between 0 and n ``DeliveryAddress``.

  It can be created using:

  .. code-block:: python

    def _create_shopinvader_delivery_address(self, vals: dict) -> "ResPartner":

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_delivery_address(self, vals: dict, address_id: int) -> "ResPartner":

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*
