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

Service must always be named in plural for example


```python
    class SaleService(Component):
        _inherit = "shopinvader.abstract.sale.service"
        _name = "shopinvader.sale.service"
        _usage = "sales"
        _expose_model = "sale.order"
```

In some really rare case your API is a singleton,
this mean work on only record without specifying the id
In that case and only in that case you can use singular
to make it explicit.
For now we have only 2 cases of singleton API customer and cart


```python
    class CartService(Component):
        _inherit = "shopinvader.abstract.sale.service"
        _name = "shopinvader.cart.service"
        _usage = "cart"
```
