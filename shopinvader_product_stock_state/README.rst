.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Shopinvader Product Stock State
================================

This is shopinvader product stock state module.
This module is used to export the stock state of product
only if the value has been updated.

Configuration
=============

Go into shopinvader > backend, and on the backend you can choose the mode
- State and Low Quantity (only add the qty if it behind a defined value)
- State and Quantity
- Only State
- Only Quantity


Usage
=====
Instead of having only the qty in the json sent to the search engine
You will have (depending of the configuration, the qty and the state)


.. code-block:: python

    example :
        {'global': {
            'state': 'in_limited_stock',
            'qty': 5.0,
        }}


Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/akretion/shopinvader/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sebastien BEAU <sebastien.beau@akretion.com>
* Simone Orsi <simahawk@gmail.com>

Funders
-------

The development of this module has been financially supported by:

* Akretion R&D
