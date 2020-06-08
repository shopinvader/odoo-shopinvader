[![Build Status](https://travis-ci.org/shopinvader/odoo-shopinvader.svg?branch=10.0)](https://travis-ci.org/shopinvader/odoo-shopinvader)
[![codecov](https://codecov.io/gh/shopinvader/odoo-shopinvader/branch/10.0/graph/badge.svg)](https://codecov.io/gh/shopinvader/odoo-shopinvader/branch/10.0)
[![Code Climate](https://codeclimate.com/github/shopinvader/odoo-shopinvader/badges/gpa.svg)](https://codeclimate.com/github/shopinvader/odoo-shopinvader)


ShopInvader
=================

Web alternative solution based on locomotivecms

Documentation
===============

The official documentation is available here: https://doc.shopinvader.com


Guideline
==============

Naming service
---------------

Services must always be named in plural form. Example:


```python
    class SaleService(Component):
        _inherit = "shopinvader.abstract.sale.service"
        _name = "shopinvader.sale.service"
        _usage = "sales"
        _expose_model = "sale.order"
```

In some rare cases where you need to expose a singleton,
you can use singular to make it explicit.

At the moment we have only 3 cases of singleton API:

- customer
- cart
- guest

Finally, working on one record at once allows to skip passing its ID around.


```python
    class CartService(Component):
        _inherit = "shopinvader.abstract.sale.service"
        _name = "shopinvader.cart.service"
        _usage = "cart"
```
