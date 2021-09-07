Essentially, call _compute_images whenever you want to refresh all image thumbnails/resizes
on your records. Resized images are then accessible through the "images" serialized field.

For an example of full implementation on a new model, you can view shopinvader_banner.
