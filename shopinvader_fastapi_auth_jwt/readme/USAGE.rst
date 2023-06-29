This module provide the following FastAPI dependencies:

``def auth_jwt_authenticated_or_anonymous_partner() -> Partner``

  This dependency returns the authenticated partner from ``fast_api_auth_jwt``
  ``auth_jwt_optionally_authenticated_partner``. If not authenticated or no partner is
  found, look for the ``shopinvader_anonymous_partner`` cookie in the request and return
  the corresponding partner.

  If not partner is found, raise a 401 (unauthorized).

``def auth_jwt_authenticated_or_anonymous_partner_auto_create() -> Partner``

  This dependency returns the authenticated partner from ``fast_api_auth_jwt``
  ``auth_jwt_optionally_authenticated_partner``. If not authenticated or no partner is
  found, look for the ``shopinvader_anonymous_partner`` cookie in the request and return
  the corresponding partner.

  If no partner is found, create an anonymous partner, set the corresponding cookie and
  return the newly created partner.

The record sets returned from these functions are bound either to the Odoo user defined
on the JWT validaator (if authenticated), or to the Odoo user defined on the FastAPI
endpoint.

These dependencies are suitable and intended to override the
``odoo.addon.fastapi.dependencies.authenticated_partner_impl``.
