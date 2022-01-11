# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    jwt_aud = fields.Char(
        string="JWT audience",
        help="Use this backend when the JWT aud claim matches this.",
    )

    def _ensure_jwt_aud(self, aud):
        """Ensure aud is valid on self

        Returns self if aud is valid
            else an empty recordset
        """
        self.ensure_one()
        if not aud:
            return self.browse([])
        if isinstance(aud, str):
            aud = [aud]
        if self.jwt_aud in aud:
            return self
        _logger.warning(
            "Inconsistency between provided backend"
            " and audience in jwt: "
            f"Backend {self.name} ({self.jwt_aud} != {aud})"
        )
        return self.browse([])
