===================
Shopinvader Address
===================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:1e8a1bd298725784f2b542c2c513ca828a5109d059d913b6fcfbc6cf17b8e19d
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-shopinvader%2Fodoo--shopinvader-lightgray.png?logo=github
    :target: https://github.com/shopinvader/odoo-shopinvader/tree/16.0/shopinvader_address
    :alt: shopinvader/odoo-shopinvader

|badge1| |badge2| |badge3|

This addons adds helper methos on the res.partner model that ease the management
and the creation of addresses within odoo code.

**Table of contents**

.. contents::
   :local:

Usage
=====

InvoicingAddress
  In the context of shopinvader, the ``InvoicingAddress`` corresponds to the authenticated partner itself.
  Therefore, the ``Invoicing Address`` is unique for each partner.

  Creation of ``Invoicing Address`` is not supported since it corresponds to the authenticated partner.

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_invoicing_address(self, vals: dict, address_id: int) -> "ResPartner"

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*

DeliveryAddress
  In the context of shopinvader, a ``DeliveryAddress`` corresponds to any delivery address linked to the authenticated partner.
  A partner can have between 0 and n ``DeliveryAddress``.

  It can be created using:

  .. code-block:: python

    def _create_shopinvader_delivery_address(self, vals: dict) -> "ResPartner":

  It can be updated using:

  .. code-block:: python

    def _update_shopinvader_delivery_address(self, vals: dict, address_id: int) -> "ResPartner":

  *Remark: it cannot be modified if it has already been used on a confirmed sale order.*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/shopinvader/odoo-shopinvader/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/shopinvader/odoo-shopinvader/issues/new?body=module:%20shopinvader_address%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* ACSONE SA/NV

Contributors
~~~~~~~~~~~~

* Laurent Mignon <laurent.mignon@acsone.eu>
* Marie Lejeune <marie.lejeune@acsone.eu>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Zina Rasoamanana <zina.rasoamanana@acsone.eu>

Maintainers
~~~~~~~~~~~

This module is part of the `shopinvader/odoo-shopinvader <https://github.com/shopinvader/odoo-shopinvader/tree/16.0/shopinvader_address>`_ project on GitHub.

You are welcome to contribute.
