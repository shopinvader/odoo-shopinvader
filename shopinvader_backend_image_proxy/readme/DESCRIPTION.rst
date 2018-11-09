This addon is used to replace the url (only the first part, without the
file name) of images serialized field of the
shopinvader.image.mixin abstract model.
Only the related recordset (who inherit this abstract model) has a
backend_id field (M2O to shopinvader.backend) and if image_proxy_url is filled.


Features:

* Add 'image_proxy_url' field into shopinvader.backend.
* If the field is set, the url will be replaced.
