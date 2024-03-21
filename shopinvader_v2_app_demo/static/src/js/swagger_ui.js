odoo.define("shopinvader_v2_app_demo.swagger_ui", function (require) {
    "use strict"; // eslint-disable-line strict

    var swagger_ui = require("base_rest.swagger_ui");

    var SwaggerUI = swagger_ui.include({
        start: function () {
            this._super.apply(this, arguments);
            this.ui.initOAuth({
                clientId: "demo16.shopinvader.com",
            });
        },
    });

    return SwaggerUI;
});
