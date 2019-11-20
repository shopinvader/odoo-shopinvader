This is shopinvader the odoo module for the new generation of e-commerce.

This module adds the field `variant_selector` in the product variant metadata (exported to algolia or elastic). 
The value of the field contains the possible combinations of variants that are available.
This ease frontend development of variant selectors.


Example of value

.. code-block:: python

    [
        {
            "name": "Color",
            "values": [
                {
                    "name": "White",
                    "sku": "White-32 GB-42 GHz",
                    "selected": True,
                    "available": True,
                },
                {
                    "name": "Black",
                    "sku": "Black-16 GB-2.4 GHz",
                    "selected": False,
                    "available": True,
                },
            ],
        },
        {
            "name": "Memory",
            "values": [
                {
                    "name": "16 GB",
                    "sku": "White-16 GB-2.4 GHz",
                    "selected": False,
                    "available": True,
                },
                {
                    "name": "32 GB",
                    "sku": "White-32 GB-42 GHz",
                    "selected": True,
                    "available": True,
                },
            ],
        },
        {
            "name": "Wi-Fi",
            "values": [
                {
                    "name": "2.4 GHz",
                    "sku": "",
                    "selected": False,
                    "available": False,
                },
                {
                    "name": "42 GHz",
                    "sku": "White-32 GB-42 GHz",
                    "selected": True,
                    "available": True,
                },
            ],
        },
    ]


This is the Odoo side of Shopinvader_.

.. _Shopinvader: https://shopinvader.com
