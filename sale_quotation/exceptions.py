# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.exceptions import UserError


class InvalidQuotationStateError(UserError):
    """Exception raised when an operation is attempted on a quotation
    that is not in the expected state.
    """

    def __init__(self, env, action, expected_states, current_state):
        self.env = env
        message = _(
            "Cannot perform '%(action)s' on quotation in state '%(current_state)s'. "
            "Expected states: '%(expected_states)s'.",
            action=action,
            expected_states=", ".join(expected_states),
            current_state=current_state,
        )
        super().__init__(message)
