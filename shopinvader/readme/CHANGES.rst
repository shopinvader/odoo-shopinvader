Changelog
---------

Future (?)
~~~~~~~~~~


14.0.3.0.0
~~~~~~~~~~~~

**Breaking change**


For historical reason (first implementation with algolia)
- the id of the binding was added in the index
- and for elastic/algolia the objectID (= the id of the record bound) was also added

This lead to a uncomprehensible situation where the frontend dev have an "id" and an "objectID" with different value and have no idea of which one should be used for filtering

Now you should use the key id in your template instead of "objectID"

Note: if you use Algolia as search engine the objectID is still here but don't use it in the template, it's only mandatory for the sync between Odoo and Algolia


See issue shopivader issue `#1000 <https://github.com/shopinvader/odoo-shopinvader/issues/1000>`_


12.0.2.0.0
~~~~~~~~~~

- index field name is now a computed field based on the backend name, the model exported and the lang
- remove dependency on keychain
- Improve UI on search engine backend (domain on model and exporter...)
- improve test coverage
- use black for auto code style
