# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.job import Job
from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderResetExpiredPassword(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderResetExpiredPassword, cls).setUpClass()
        cls.backend.password_validity = 10
        cls.partner = cls.env.ref("shopinvader.shopinvader_partner_1")
        cls.partner.last_pwd_reset_datetime = "2019-12-31 12:00:00"

    def test_reset_expired_password(self):
        # Simulate cron call
        # Check if one job is created per backend with activated validity delay
        # Run the job and check if reset password is done
        self._init_job_counter()
        self.backend._launch_reset_expired_password()
        self._check_nbr_job_created(1)
        created_job = self.created_jobs
        self._init_job_counter()
        Job.load(self.env, created_job.uuid).perform()
        # The reset password job + the export to locomotive
        self._check_nbr_job_created(2)
