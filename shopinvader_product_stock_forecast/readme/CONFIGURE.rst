On the Shopinvader Backend, enable the **Stock Forecast**.

Optionally, you can set a **Stock Forecast Horizon** in days to limit the
number of days to forecast.

.. warning::

    The `shopinvader_product_stock` module will let you use a different field other than
    `qty_available` to export the current stock.

    The forecast may not make sense if you don't have the proper stock to start with, so
    it's recommended not to use a different field there.
