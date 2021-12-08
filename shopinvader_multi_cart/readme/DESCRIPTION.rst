This allows to manage multiple carts per user.

It exposes a new service `carts` to fetch the user's saved carts, read them,
delete them, or select any of them as the current cart.

It also adds a new method `save` on the `cart` service, to store the current
cart. It can later be accessed and eventually restored from the `carts` service.

Saved carts are identified with the typology `saved`.
