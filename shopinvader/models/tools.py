# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
except ImportError:
    _logger.debug("Cannot `import unidecode`.")


def sanitize_attr_name(attribute):
    key = attribute.name
    return unidecode(key.replace(" ", "_").lower())
