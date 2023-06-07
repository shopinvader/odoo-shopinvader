The following model methods are added to ``res.partner``:

``_create_anonymous_partner(response)``

  Create a new anonymous partner and set the ``shopinvader-anonymous-partner`` cookie.
  Return the newly created partner record.

  ``response`` is typically the http response, it must have a ``set_cookie()`` method.
  It is known to work with ``odoo.http.request.future_response`` and FastAPI
  ``Response`` objects.

``_get_anonymous_partner(cookies)``

  Return the partner record corresponding to the ``shopinvader-anonymous-partner``
  cookie in the current request, if any. Returns an empty record set if the cookie is
  not set or if the corresponding partner was not found.

  ``cookies`` is the cookies dictionary from the http request.

Note the record sets returned by these methods are in a sudo'ed environment, so handle
with care.
