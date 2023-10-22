This module adds new cart routes to do batch operations on cart items.

The new routes are as follows:

* ``POST /cart/add_items`` - Add new items to the cart
* ``POST /cart/update_items`` - Update existing items in the cart
* ``POST /cart/remove_items`` - Remove items from the cart


The parameters for each route are the same as the existing ``POST /cart`` route but inside a ``batch`` parameter::

  {
    "batch": [
      {
        "item_id": 1,
        "item_qty": 2
      },
      {
        "item_id": 2,
        "item_qty": 3
      }
    ]
  }
