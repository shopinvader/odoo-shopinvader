This is shopinvader the odoo module for the new generation of e-commerce.

This module adds the field `variant_selector` in the product variant metadata (exported to algolia or elastic).
The value of the field contains the possible combinations of variants that are available.
This ease frontend development of variant selectors.


Example of value
---------------------


.. code-block:: python

    [
        {
            "name": "Frame Type",
            "values": [
                {
                    "name": "Poster",
                    "sku": "Poster-White-70x50cm",
                    "selected": True,
                    "available": True,
                },
                {
                    "name": "Wooden",
                    "sku": "Wooden-White-70x50cm",
                    "selected": False,
                    "available": True,
                },
            ],
        },
        {
            "name": "Frame Color",
            "values": [
                {
                    "name": "White",
                    "sku": "Poster-White-70x50cm",
                    "selected": True,
                    "available": True,
                },
                {
                    "name": "Black",
                    "sku": "Poster-Black-70x50cm",
                    "selected": False,
                    "available": True,
                },
                {
                    "name": "Grey",
                    "sku": "Poster-Grey-70x50cm",
                    "selected": False,
                    "available": True,
                },

            ],
        },
        {
            "name": "Poster Size",
            "values": [
                {
                    "name": "45x30cm",
                    "sku": "",
                    "selected": False,
                    "available": False,
                },
                {
                    "name": "70x50cm",
                    "sku": "Poster-White-70x50cm",
                    "selected": True,
                    "available": True,
                },
                {
                    "name": "90x60cm",
                    "sku": "Poster-White-90x60cm",
                    "selected": False,
                    "available": True,
                },
            ],
        },
    ],

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
