This addons adds a new option on the Shopnvader backend to allow to sale orders
in guest mode. The guest mode is a special case on the ecommerce website where
the customer is allowed to create a sale order without creating of a user
account on the website.

Into Odoo this results in the creation of a partner + binding with a fixed
validity period linked to the sale order. At the end of this period, the
binding is automatically disabled if the customer has not created an account.

It's not possible to create a new customer with the same email if a binding is
valid. In such a case the customer must create an account

If a customer create a new sale order in guest mode with the
same email, the new partner will be linked to the first partner found with
the same email except if shopinvader is configured to avoid duplicate partners
