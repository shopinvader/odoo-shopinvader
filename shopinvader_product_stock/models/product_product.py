# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.addons.queue_job.job import job


class ProductProduct(models.Model):
    _inherit = "product.product"

    @job(default_channel="root.search_engine.synchronize_stock")
    def _synchronize_all_binding_stock_level(self):
        """
        The goal of this function is to compute the new stock information
        and update them in the data field. If data have change and the binding
        is in done state we force it to 'to_update'.
        :return:
        """
        all_bindinds = self.mapped("shopinvader_bind_ids")
        backends = all_bindinds.mapped("backend_id")
        for backend in backends:
            bindings = all_bindinds.filtered(
                lambda r, b=backend: r.backend_id == b
            )
            # To avoid access rights issues, execute the job with the user
            # related to the backend
            bindings = bindings.with_user(backend.user_id.id)
            for binding in bindings:
                if binding.sync_state == "new":
                    # this binding have been not yet computed
                    # so we do not care to update it as it's not yet
                    # on the site. The right stock qty will be exported
                    # at it's first export
                    continue
                # I do not recommend to rename the stock export key, but if
                # you have a good reason to do it, do not worry we will use
                # this key here
                stock_export_key = binding._get_stock_export_key()
                if not stock_export_key:
                    continue
                data = binding.data
                if data[stock_export_key] != binding.stock_data:
                    data[stock_export_key] = binding.stock_data
                    vals = {"data": data}
                    if binding.backend_id.synchronize_stock == "immediatly":
                        binding.write(vals)
                        binding.synchronize()
                    elif binding.backend_id.synchronize_stock == "in_batch":
                        if binding.sync_state == "done":
                            vals["sync_state"] = "to_update"
                        binding.write(vals)
