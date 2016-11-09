# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging

_logger = logging.getLogger(__name__)


class Testbaseurl(SingleTransactionCase):

    def setup(self):
        super(Testbaseurl, self).setup()

    def test__get_reference(self):
        product = self.env['product.template'].browse(9)
        model_ref = product._get_model_id_reference()
        model = "%s,%s" % (product._name, product.id)
        self.assertEqual(model, model_ref)
        self.assertEqual("product.template,9", model_ref)

    def test_change_name(self):
        product = self.env['product.template'].browse(9)

        product.name = u"Un Joli épervier"

        product.on_name_change()

        # product._inverse_set_url()

        np = self.env['url.url'].search(
            [('model_id', '=', "product.template,9"),
             ('redirect', '=', False)])
        _logger.info(u"url_key len  : %s ", len(np))

        url_key = np.url_key
        _logger.info(u"url_key : %s ", url_key)
        self.assertTrue(len(np) == 1)
        self.assertEqual('un-joli-epervier', url_key)

    def test_change_url_key(self):
        product = self.env['product.template'].browse(9)

        product.url_key = u"Un Joli épervier"
        product.on_url_key_change()

        product._inverse_set_url()

        url_key = self.env['url.url'].search([
            ('model_id', '=', "product.template,9"),
            ('redirect', '=', False)]).url_key

        _logger.info(u"url_key : %s ", url_key)

        self.assertEqual('un-joli-epervier', url_key)

    def test_onchange_url_key(self):
        product = self.env['product.template'].browse(9)

        product.url_key = u"Un Joli épervier"
        res = product.on_url_key_change()

        _logger.debug(res['warning'],)

        self.assertEqual('it will will be adapted to un-joli-epervier',
                         res['warning']['message'])

    def test_get_object(self):
        product = self.env['product.template'].browse(9)
        product.name = u"Un Joli épervier"

        product.on_name_change()
        product._inverse_set_url()
        url1 = self.env['url.url'].search([
            ('model_id', '=', "product.template,9"),
            ('redirect', '=', False)]).url_key

        product.url_key = u"De Jolie éperviere"  # (de-jolie-eperviere)
        product._inverse_set_url()
        url2 = self.env['url.url'].search([
            ('model_id', '=', "product.template,9"),
            ('redirect', '=', False)]).url_key

        _logger.info("les url: %s %s " % (url1, url2))
        urlurl1 = self.env['url.url']._get_object(url1)

        urlurl2 = self.env['url.url']._get_object(url2)

        self.assertEqual(urlurl1, urlurl2)
