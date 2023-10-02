This module focus on the serialization of brand information into JSON objects
in the context of the `Shopinvader`_ project. These information are mainly used
to be made available for a `Shopinvader`_ website through an export to search
engine indexation services like ElasticSearch / OpenSearch.

* It defines a new specific Pydantic model to be used to serialize a *product.brand*
  record into a JSON object.

* It extends the ProductProduct Pydantic model to add the brand information in the
  JSON exported for a product.product record.

.. _Shopinvader: https://shopinvader.com
