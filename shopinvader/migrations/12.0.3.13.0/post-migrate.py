# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Group Queue Job Manager should be updated"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    job_manager = env.ref("queue_job.group_queue_job_manager")
    shop_manager = env.ref("shopinvader.group_shopinvader_manager")
    job_manager.implied_ids -= shop_manager
