This addon adds a web API to signin into the application and create a partner
if the email in the jwt payload is unknown.

This addon supports the "anonymous partner" feature, which allows to create
carts for user that are not loggedin.
When you login from an anonymous partner, your cart is transfered to your real
partner, and your anonymous partner is deleted.
