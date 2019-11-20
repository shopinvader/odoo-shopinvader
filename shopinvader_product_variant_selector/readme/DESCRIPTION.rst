This is shopinvader the odoo module for the new generation of e-commerce.

This module adds the field `variant_selector` in the product variant metadata (exported to algolia or elastic).
The value of the field contains the possible combinations of variants that are available.
This ease frontend development of variant selectors.


Example of value
---------------------


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

Undertanding the way to select attribute
------------------------------------------------

It's also important to understand how variant are selected and how attribute value are filtered.

Imaging a case where you have a child shoes with
- 6 sizes: 15, 16, 17, 18, 19, 20
- 3 colors: Green, Red, Yellow

It's a special shoes:
- Green exist in size: 18, 19
- Red exist in size: 15, 16, 17
- Yellow exist in size: 18, 19, 20

In your ERP you have configured to select is the size then the color.
And the default variant is the first "Green 18"

Step 1 : You go to the page of your product.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will have:

.. code-block:: python

    size : 15, 16, 17, [18], 19, 20
    color : [Green], (Red), Yellow

    [] mean selected
    () mean not available


Only the color Green and Yellow are available because the size 18 is selected.


Step 2: Now you select the color Yellow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will have:

.. code-block:: python

    size : 15, 16, 17, [18], 19, 20
    color : Green, (Red), [Yellow]

Even if you select the color Yellow the size are now filetered because the second filter can not filter the first one.


Step 3: Now you select the size 16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As only the Red color is available for this size you are redirected to the Red shoes and you have

.. code-block:: python

    size : 15, [16], 17, 18, 19, 20
    color : (Green), [Red], (Yellow)


Why not trying to filter the size when changing the color?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because if we do this if you select the size 16

Then you will have this

.. code-block:: python

    size : 15, [16], 17, (18), (19), (20)
    color : (Green), [Red], (Yellow)


And you will be locked in this situation without any possibility to select the Yellow shoes with size 19. There is an order for filling/selected the value of each option and selecting a value should only impact the next attribute not the previous one.


This is the Odoo side of Shopinvader_.

.. _Shopinvader: https://shopinvader.com
