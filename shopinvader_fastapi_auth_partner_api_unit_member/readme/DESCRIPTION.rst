This module glues the `shopinvader_fastapi_auth_partner_api` and the `shopinvader_api_unit_member` modules.
 
It adds a auth_state field to the unit member and defines this member route:

- `POST /unit/members/:id/invite` to add an auth.partner to the unit member allowing it to sign in and send an invite email to it.

