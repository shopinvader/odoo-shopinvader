This module exports the forecasted stock quantities for each product.
This data can be used by the frontend to compute virtual stocks at any given date.

The stock forecast data is a list of planned stock variations, like so:

.. code-block:: python

    [
        {"date": "2021-12-01T08:00:00", "qty": 10},
        {"date": "2021-12-02T10:00:00", "qty": -1},
        {"date": "2021-12-03T15:00:00", "qty": -4},
        {"date": "2021-12-04T11:00:00", "qty": 5},
    ]


This data can be used by aggregated and used by the frontend to compute the virtual
stock of a product at any given date.

For example, assuming the initial `qty_available` is `10`, and that today is
`2021-12-01 00:00:00`, we can infer the following:

* After `2021-12-01 08:00:00`, stock will be `20`
* After `2021-12-02 10:00:00`, stock will be `19`
* After `2021-12-03 15:00:00`, stock will be `15`
* After `2021-12-04 11:00:00`, stock will be `20`
