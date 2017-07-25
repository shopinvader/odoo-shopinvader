# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import secure_params, ShopinvaderService
from .cart import CartService
from ..backend import shopinvader
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


@shopinvader
class TransactionService(ShopinvaderService):
    _model_name = 'gateway.transaction'

    @secure_params
    def get(self, params):
        provider = self._get_provider(params)
        if provider is not None:
            transaction = provider._get_transaction_from_return(params)
            transaction.check_state()
            if transaction.state in ['to_capture', 'succeeded']:
                cart_service = self.service_for(CartService)
                # confirm the card
                data = cart_service.update({
                    'next_step': self.backend_record.last_step_id.code})
                data['redirect_to'] = transaction.redirect_success_url
                return data
            else:
                return {
                    'redirect_to': transaction.redirect_cancel_url,
                    'store_cache': {
                        'notifications': [{
                            'type': 'danger',
                            'message': _('Paiment failed please retry'),
                        }]
                    }
                }
        _logger.error('Shopinvader: Transaction params are invalid')
        return {'redirect_to': self.backend_record.location}

    # Validator
    def _validator_get(self):
        validator = {}
        for provider in self.env['payment.service']._get_all_provider():
            if hasattr(self.env[provider], '_return_validator'):
                validator.update(self.env[provider]._return_validator())
        return validator

    def _get_provider(self, params):
        for provider in self.env['payment.service']._get_all_provider():
            provider_obj = self.env[provider]
            if hasattr(provider_obj, '_transaction_match'):
                if provider_obj._transaction_match(params):
                    return provider_obj
