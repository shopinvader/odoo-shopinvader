This module adds a service to shopinvader to manage units members: managers and collaborators.

A manager can list, create, update and delete collaborators. 

The router defines these routes:

- `GET /unit/members` to list collaborators
- `GET /unit/members/:id` to get a collaborator
- `POST /unit/members` to create a collaborator
- `POST /unit/members/:id` to update a collaborator
- `DELETE /unit/members/:id` to delete a collaborator

