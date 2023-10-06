odoo.define("shopinvader_v2_app_demo.swagger_ui", function (require) {
    "use strict"; // eslint-disable-line strict

    var swagger_ui = require("base_rest.swagger_ui");

    var SwaggerUI = swagger_ui.include({
        _swagger_bundle_settings: function () {
            const defaults = this._super.apply(this, arguments);
            const config = {
                oauth2RedirectUrl:
                    window.location.origin + "/shopinvader_jwt/docs/oauth2-redirect",
            };
            return Object.assign({}, defaults, config);
        },
    });

    return SwaggerUI;
});
