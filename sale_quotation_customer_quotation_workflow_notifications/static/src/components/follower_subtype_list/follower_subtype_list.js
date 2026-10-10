/** @odoo-module **/

import {FollowerSubtypeList} from "@mail/components/follower_subtype_list/follower_subtype_list";
import {patch} from "@web/core/utils/patch";

import {useState} from "@odoo/owl";

function getUrlSearchParams() {
    return new URLSearchParams(location.hash.substring(1));
}
patch(
    FollowerSubtypeList.prototype,
    "Add a filter on message subtypes for customer quotation sale orders",
    {
        async setup() {
            this._super();

            this.state = useState({
                filteredSubtypeViews: this.followerSubtypeList.followerSubtypeViews,
            });

            this.state.filteredSubtypeViews = await this.filteredFollowerSubtypeViews();
        },

        async filteredFollowerSubtypeViews() {
            const urlSearchParams = getUrlSearchParams();
            if (
                urlSearchParams.get("model") != "sale.order" ||
                urlSearchParams.get("view_type") != "form"
            ) {
                return this.followerSubtypeList.followerSubtypeViews;
            }

            const records = await this.env.services.orm.searchRead(
                "sale.order",
                [["id", "=", urlSearchParams.get("id")]],
                ["use_customer_quotation_workflow"]
            );
            const record = records.length ? records[0] : null;

            if (!record || !record.use_customer_quotation_workflow) {
                return this.followerSubtypeList.followerSubtypeViews.filter(
                    (x) =>
                        x.subtype.resModel === false || x.subtype.parentModel === false
                );
            }
            return this.followerSubtypeList.followerSubtypeViews.filter(
                (x) => x.subtype.resModel !== false && x.subtype.parentModel !== false
            );
        },
    }
);

patch(FollowerSubtypeList, "Filter subtypes on sale orders", {
    template:
        "sale_quotation_customer_quotation_workflow_notifications.FilteredFollowerSubtypeList",
});
