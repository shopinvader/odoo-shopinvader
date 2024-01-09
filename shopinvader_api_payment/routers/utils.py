# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


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
