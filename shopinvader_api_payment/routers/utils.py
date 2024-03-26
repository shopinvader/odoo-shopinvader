# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import urlparse, urlunparse

import jwt
from pydantic import BaseModel

from odoo.api import Environment


class Payable(BaseModel):
    payable_id: int
    payable_model: str
    payable_reference: str
    amount: float
    currency_id: int
    partner_id: int
    company_id: int
    transaction_id: int | None = None

    @classmethod
    def _get_secret(cls, env: Environment) -> str:
        secret = env["ir.config_parameter"].sudo().get_param("database.secret")
        if not secret:
            raise ValueError("Missing database secret")
        return secret

    def encode(self, env: Environment) -> str:
        """Encode the payable as a JWT token, signed with the database secret."""
        payload = self.model_dump()
        return jwt.encode(
            payload=payload,
            key=self._get_secret(env),
            algorithm="HS256",
        )

    @classmethod
    def decode(cls, env: Environment, encoded: str) -> "Payable":
        """Verify and decode a payable encoded as JWT token."""
        payload = jwt.decode(
            jwt=encoded,
            key=cls._get_secret(env),
            algorithms=["HS256"],
        )
        return cls.model_validate(payload)


def add_query_params_in_url(base_url, params):
    """
    Parse and unparse base_url to add params as query params in this url.
    :param params: a dict of query parameters
    """
    parsed_url = urlparse(base_url)
    query = parsed_url.query
    params_encoded = "&".join([f"{param}={value}" for param, value in params.items()])
    all_params_encoded = f"{query}&{params_encoded}" if query else f"{params_encoded}"
    return urlunparse(parsed_url._replace(query=all_params_encoded))


def tx_state_to_redirect_status(tx_state):
    """Map a transaction state to a redirect status."""
    if tx_state == "done":
        return "success"
    elif tx_state == "cancel":
        return "cancelled"
    elif tx_state == "pending":
        return "pending"
    else:
        return "unknown"
