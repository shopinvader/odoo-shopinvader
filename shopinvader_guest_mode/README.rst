.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Shopinvader Guest Mode
======================

This addons adds a new option on the Shopnvader backend to allow to sale orders
in guest mode. The guest mode is a special case on the ecommerce website where
the customer is allowed to create a sale order without creating of a user
account on the website.

Into Odoo this results in the creation of a partner + binding with a fixed
validity period linked to the sale order. At the end of this period, the
binding is automatically disabled if the customer has not created an account.

It's not possible to create a new customer with the same email if a binding is
valid. In such a case the customer must create an account

If a customer create a new sale order in guest mode with the
same email, the new partner will be linked to the first partner found with
the same email except if shopinvader is configured to avoid duplicate partners

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* laurent.mignon <laurent.mignon@acsone.eu>

Funders
-------

The development of this module has been financially supported by:

* Abitare

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
