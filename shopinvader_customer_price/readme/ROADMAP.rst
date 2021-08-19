Probably the best option would be to have 1 index per customer
which would even allow to sort and filter products by customer's prices
but this requires a lot of work with current implementation of search engine machinery.

If you use Algolia this is probably a no-go as it would cost too much.
In the context of ElasticSearch instead you could afford it.

Things that would be needed to go for an indexed solution:

* make language not required on indexes (at the momemt the whole SE machinery relies on languages)
* automatically generate one index per each pricelist/customer
* make the frontend capable of switching indexes depending on the customer
