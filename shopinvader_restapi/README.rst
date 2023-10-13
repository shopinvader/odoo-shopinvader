===========
Shopinvader
===========

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-shopinvader%2Fodoo--shopinvader-lightgray.png?logo=github
    :target: https://github.com/shopinvader/odoo-shopinvader/tree/14.0/shopinvader
    :alt: shopinvader/odoo-shopinvader

|badge1| |badge2| |badge3| 

This is shopinvader the odoo module for the new generation of e-commerce.

ShopInvader is an ecommerce software to create and manage easily your online store with Odoo.

This is the Odoo side of the `Shopinvader E-commerce Solution`_.

.. _Shopinvader E-commerce Solution: https://shopinvader.com

**Table of contents**

.. contents::
   :local:

Known issues / Roadmap
======================

* Customer validation limitation

Customer validation is global: enable/disable affects all websites, if you have more than one.

Technical
~~~~~~~~~

* Create methods should be rewritten to support multi
*  The logic to bind / unbind products and categories should be implemented as
   component in place of wizard.
   Previously it was possible to work with in-memory record of the wizard to
   call the same logic from within odoo. In Odoo 13 it's no more the case.
   That means that to rebind thousand of records we must create thousand of
   rows into the database to reuse the logic provided by the wizard.
*  On product.category the name is no more translatable in V13.
   This functionality has been restored into shopinvader.
   This should be moved into a dedicated addon

Changelog
=========

10.0.1.0.0 (2017-04-11)
~~~~~~~~~~~~~~~~~~~~~~~

* First real version : [REF] rename project to the real name : shoptor is dead long live to shopinvader", 2017-04-11)

12.0.1.0.0 (2019-05-10)
~~~~~~~~~~~~~~~~~~~~~~~

* [12.0][MIG] shopinvader

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/shopinvader/odoo-shopinvader/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/shopinvader/odoo-shopinvader/issues/new?body=module:%20shopinvader%0Aversion:%2014.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Akretion

Contributors
~~~~~~~~~~~~

* Sebastien BEAU <sebastien.beau@akretion.com>
* Simone Orsi <simone.orsi@camptocamp.com>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Raphaël Reverdy <raphael.reverdy@akretion.com>
* Kevin Khao <kevin.khao@akretion.com>

Other credits
~~~~~~~~~~~~~

The development of this module has been financially supported by:

* Akretion
* Adaptoo
* Encresdubuit
* Abilis
* Camptocamp
* Cosanum

Maintainers
~~~~~~~~~~~

This module is part of the `shopinvader/odoo-shopinvader <https://github.com/shopinvader/odoo-shopinvader/tree/14.0/shopinvader>`_ project on GitHub.

You are welcome to contribute.