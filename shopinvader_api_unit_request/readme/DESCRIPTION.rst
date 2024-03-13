This module adds the possibility to make a request from a cart as
a collaborator of a unit to be later reviewed, merged and converted into a 
sale order by a unit manager.

The `cart_router` has been extended to allow the creation of a request:

- `POST /api/cart/request` to create a request from the current cart.
- `POST /api/cart/current/request` to create a request from the current cart.
- `POST /api/cart/:uuid/request` to create a request from a specific cart.

The `sale_router` has been extended to allow the /api/sale_lines to also list the requested sale lines.

A new `unit_request_line_router` has been added to manage the requests:

- `GET /api/unit_request_lines` to list the requested lines.
- `GET /api/unit_request_lines/:id` to get a specific requested line.
- `POST /api/unit_request_lines/:id/accept` to accept a requested line.
- `POST /api/unit_request_lines/:id/reject` to reject a requested line.
- `POST /api/unit_request_lines/:id/reset` to reset the rejected status of a requested line.

NB: The deletion of an accepted line in the manager cart will put it back in the request.
