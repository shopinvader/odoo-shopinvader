This module will export the price per qty into you index.


You will have an extra key "per_qty" in the existing "price" key with the price per quantity value

For example

.. code-block:: python

    "price": {
        "value": XXX,
        "tax_included": XXX,
        "original_value": XXX,
        "discount": XXX,
        "per_qty": {10.0: 456.52, 20.0: 391.3, 30.0: 326.09, 40.0: 260.87}

Note : in case that you have a lot of pricelist, this can be perf costly
