To enable anonymous carts, you'll need the module
`shopinvader_fastapi_auth_jwt`. And use it's dependency
`auth_jwt_authenticated_or_anonymous_partner_autocreate` when mounting
your cart router, such as:

``` python
cart_app = FastAPI()
cart_app.include_router(cart_router)
cart_app.dependency_overrides.update(
    {
        authenticated_partner_impl: auth_jwt_authenticated_or_anonymous_partner_autocreate,
    }
)
```

Example of a full implementation with jwt signin and anonymous carts can
be found in the demo module `shopinvader_v2_app_demo`.
