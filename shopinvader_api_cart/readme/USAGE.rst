All the routes under the `cart_router` must be prefixed with `/cart`.
This is not done in this addon to let the developper mount
this router as a sub-app, allowing a specific authentification mechanism.

If mounting the router in the same app as other routers (because it doesn't need a specific authentification mechanism), just add a prefix:

 .. code-block:: python

    def _get_app(self):
       app = super()._get_app()
       app.include_router(router=cart_router, prefix='/cart')
       return app

If you want a nested app, just do as follows:

 .. code-block:: python

    def _get_app(self):
        app = super()._get_app()
        app.dependencies_overrides.update(
            self._get_app_dependencies_overrides()
        )
        cart_app = FastAPI()
        cart_app.include_router(cart_router)
        # First copy dependencies overrides from the main app
        cart_app.dependencies_overrides.update(
            self._get_app_dependencies_overrides()
        )
        # Then add / modify specific dependencies overrides
        cart_app.dependencies_overrides.update(
             self._get_cart_app_dependencies_overrides()
        )
        app.mount("/cart", cart_app)
        return app
