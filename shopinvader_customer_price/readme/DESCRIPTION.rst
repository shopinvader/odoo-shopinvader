Handle customer specific prices.

Provides:

* endpoint `/customer_price/products` to fetch customer prices for products.
* backend configuration to state which pricelist should be used by partner
  (by selecting a partner field that relates to pricelists)


**Use case**

Thousands of customers and at least 1 pricelist per each customer.
You want to display customer specific prices in the frontend on demand.
For instance: product page, wishlists, etc.

**Rationale**

One of the key points of Shopinvader's speed
is the delegation of products' data indexing to external search engines.

While this is perfect for generic data and not so complex price rules,
if you have very special prices per each customer that's a blocker,
and you'd need to index all prices for all customers to make it work seemlessly.

**Warning**

It's strongly recommended to not call the endpoint for each product on search results
otherwise you'll get potentially thousands of requests to Odoo.

Also, when setting the pricelist field for the partner,
beware that prices in the indexes might differ from the prices in the cart.
