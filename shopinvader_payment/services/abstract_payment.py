# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AbstractPaymentService(AbstractComponent):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.abstract.payment.service'

    # Public service

    def add_payment(self, **params):
        target = self._load_target(params)
        return self._add_payment(target, params)

    def _load_target(self, params):
        """

        :param params: dict
        :return: exposed model recordset
        """
        return NotImplementedError

    def _add_payment(self, target, params):
        if not target:
            raise UserError(_('There is not target'))
        else:
            provider_name = self._set_payment_mode(target, params)
            if provider_name:
                return self._process_payment_provider(
                    provider_name, target, params.get(provider_name))
            else:
                return self._action_after_payment(target)

    def _action_after_payment(self, target):
        """
        Execute some action after the payment adding a payment
        :param target: payment recordset
        :return: dict
        """
        return {}

    def _get_target_provider(self, target):
        """

        :param target: payment recordset
        :return: str
        """
        if 'payment_mode_id' in target._fields:
            return target.payment_mode_id.provider
        return ''

    def check_payment(self, provider_name=None, **params):
        with self.env['gateway.transaction']._get_provider(provider_name)\
                as provider:
            transaction = provider.process_return(**params)
            if transaction.state in ['to_capture', 'succeeded']:
                result = self.update(
                    step={'next': self.shopinvader_backend.last_step_id.code},
                    )
                result.update({
                    'redirect_to': transaction.redirect_success_url,
                })
                return result
            else:
                return {
                    'redirect_to': transaction.redirect_cancel_url,
                    'store_cache': {
                        'notifications': [{
                            'type': 'danger',
                            'message': _('Payment failed please retry'),
                        }]
                    }
                }
        _logger.error('Shopinvader: Transaction params are invalid')
        return {'redirect_to': self.shopinvader_backend.location}

    # Validator
    def _validator_add_payment(self):
        validator = {
            'payment_mode': {
                'type': 'dict',
                'schema': {
                    'id': {
                        'coerce': int,
                        'nullable': True,
                        'required': True,
                        },
                    }
                },
            }
        for provider in self.env['gateway.transaction']._get_all_provider():
            if hasattr(provider, '_validator_add_payment'):
                validator[provider._provider_name] = {
                    'type': 'dict',
                    'schema': provider._validator_add_payment()
                    }
        return validator

    def _validator_check_payment(self):
        validator = {
            'provider_name': {
                'type': 'string',
                'required': True,
                }
            }
        # TODO the current way to retrieve the validator do not allow
        # to make set as require some field of the validator
        # we should found a better solution
        for provider in self.env['gateway.transaction']._get_all_provider():
            if hasattr(provider, '_validator_check_payment'):
                validator.update(provider._validator_check_payment())
        return validator

    # Private method
    def _set_payment_mode(self, target, params):
        """

        :param target: payment recordset
        :param params: dict
        :return: str
        """
        payment_mode_id = params.get('payment_mode', {}).get('id')
        available_payment_mode_ids = [
            x.get('id') for x in self._get_available_payment_mode(target)]
        if payment_mode_id not in available_payment_mode_ids:
            raise UserError(_('Unsupported payment mode'))
        elif 'payment_mode_id' in target._fields:
            vals = {
                'payment_mode_id': payment_mode_id,
            }
            newvals = target.play_onchanges(
                vals,
                ['payment_mode_id'],
            )
            vals.update(newvals)
            target.write(vals)
        return self._get_target_provider(target)

    def _get_return_url(self, provider_name):
        # TODO on locomotive side we expose the base path "invader"
        # On Odoo side we still use "shopinvader"
        # for next version we should use "invader" on both side
        return "%s/invader/%s/check_payment/%s" % (
            self.shopinvader_backend.location,
            self._usage, provider_name)

    def _process_payment_provider(self, provider_name, target, params):
        params['return_url'] = self._get_return_url(provider_name)
        transaction = self.env['gateway.transaction'].generate(
            provider_name, target, **params)
        return self._execute_payment_action(
            provider_name, transaction, target, params)

    def _execute_payment_action(
            self, provider_name, transaction, target, params):
        if transaction.url:
            return {'redirect_to': transaction.url}
        elif transaction.state in ('succeeded', 'to_capture'):
            self._update_target_with_transaction(target, transaction)
            return self._action_after_payment(target)
        else:
            raise UserError(_('Payment failed please retry'))

    def _update_target_with_transaction(self, target, transaction):
        """
        Based on the transaction, update some values on the target:
        - If the target has an external_id, update this field with the
        external_id of the transaction.
        :param target: recordset
        :param transaction: gateway.transaction recordset
        :return: bool
        """
        if 'external_id' in transaction._fields and transaction.external_id:
            target.transaction_id = transaction.external_id
        return True

    def _convert_one_target(self, target):
        result = {}
        if target:
            self._include_payment(target, result)
        return result

    def _include_payment(self, target, values):
        """
        Include payment details
        :param target: recordset
        :param values: dict
        :return: dict
        """
        values.update({
            'payment': self._get_payment_info(target),
        })
        return values

    def _get_payment_info(self, target):
        """

        :param target: target recordset
        :return: dict
        """
        methods = self._get_available_payment_mode(target)
        selected_method = self._get_selected_method(methods, target)
        values = {
            'available_methods': {
                'count': len(methods),
                'items': methods,
            },
            'selected_method': selected_method,
            'amount': self._get_target_total(target),
        }
        return values

    def _get_target_total(self, target):
        """
        Get the total amount to paid
        :param target: target recordset
        :return: float
        """
        return target._get_transaction_to_capture_amount()

    def _get_selected_method(self, methods, target):
        """

        :param methods: list of dict
        :param target:
        :return: dict
        """
        selected_method = {}
        if target.payment_mode_id:
            for method in methods:
                if method.get('id') == target.payment_mode_id.id:
                    selected_method = method
        return selected_method

    def _prepare_payment(self, method):
        return {
            'id': method.payment_mode_id.id,
            'name': method.payment_mode_id.name,
            'provider': method.payment_mode_id.provider,
            'code': method.code,
            'description': method.description,
        }

    def _get_available_payment_mode(self, target):
        methods = []
        for method in self.shopinvader_backend.payment_method_ids:
            methods.append(self._prepare_payment(method))
        return methods

    def _convert_one_sale(self, sale):
        values = self._convert_one_target(sale)
        values.update(super(AbstractPaymentService, self)._convert_one_sale(
            sale))
        return values
