This addon provides the legacy REST api provided by the *shopinvader* addon
in previous versions.

From version 16.0, a rework of the REST api has been started. This rework
has as goal to provide a more consistent and documented API. This rework is also
based on a new technical stack (FastAPI_, Pydantic_, extendable_pydantic_, ..).

Some endpoints provided by the legacy API are already available in the new API.

* ``cart``: The *shopinvader_api_cart* addon provides the new API for the cart
  management.
* ``address``: The *shopinvader_api_address* addon provides the new API for the
  address management.

Others endpoints will be available in the future.

The *shopinvader_v2_app_demo* addon highlights how you can aggregate the new
API and the legacy API in the same Odoo instance but also how you can combine
the different parts of the new API into a single application.

.. _FastAPI: https://fastapi.tiangolo.com/
.. _Pydantic: https://pydantic-docs.helpmanual.io/
.. _extendable_pydantic: https://pypi.org/project/extendable-pydantic/
