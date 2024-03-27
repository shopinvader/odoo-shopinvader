Integrate `product_template_multi_link` into Shopinvader.
This module takes care of computing product links data
for search engine product indexes.
Index data is computed as a mapping of variants by link type.
The link list only contains links to product linked through a
symmetric link type or product on the left side of a non-symmetric
link type. In a asymmetric link type, we take as assumption that
that the left side of the relation is the product to promote, the one
with the added value.
