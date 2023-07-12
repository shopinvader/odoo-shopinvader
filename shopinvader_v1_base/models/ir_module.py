from odoo import models


class Module(models.Model):
    _inherit = "ir.module.module"

    def _state_update(self, newstate, states_to_update, level=100):
        # try to fix installation dependency missing shopinvader
        for module in self:
            for dep in module.dependencies_id:
                if dep.name == "shopinvader":
                    dep.name = "shopinvader_v1_base"
        super()._state_update(newstate, states_to_update, level)
