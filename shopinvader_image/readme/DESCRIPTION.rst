This module allows to store product (variant) and category images
in an external system like a content delivery network (CDN).
The images will be available directly to the browser by url link.

This external system can be:
- storage object like AWS S3, Openstack Swift
- traditionnal file server (sftp, http)
- odoo
- etc.


See storage_backend_* modules from storage repository
(https://github.com/akretion/storage) to pick one of
the available storage solution.
