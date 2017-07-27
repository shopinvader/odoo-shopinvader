# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    def _get_domain_for_sale_validation(self):
        domain = super(AutomaticWorkflowJob, self).\
            _get_domain_for_sale_validation()
        domain.append(('typology', '=', 'sale'))
        return domain
