# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestBaseUrl(SingleTransactionCase):

    def setup(self):
        super(TestBaseUrl, self).setup()

    def test_change_name(self):
        product = self.env['product.template'].browse(9)

        product.name = u"Un Joli épervier"

        product.on_name_change()

        product._set_url()

        url_key = self.env['url.url'].search([('model_id', '=',
                "product.template,9"), ('redirect', '=', False)]).url_key

        print (u"url_key : %s ", url_key)

        self.assertEqual('un-joli-epervier', url_key)

    def test_change_url_key(self):
        product = self.env['product.template'].browse(9)

        product.url_key = u"Un Joli épervier"
        product._set_url()

        url_key = self.env['url.url'].search([('model_id', '=',
                "product.template,9"), ('redirect', '=', False)]).url_key
        print (u"url_key : %s ", url_key)

        self.assertEqual('un-joli-epervier', url_key)

    def test_get_object(self):
        product = self.env['product.template'].browse(9)
        product.name = u"Un Joli épervier"

        product.on_name_change()
        product._set_url()
        url1 = self.env['url.url'].search([('model_id', '=',
                "product.template,9"), ('redirect', '=', False)]).url_key

        product.url_key = u"De Jolie éperviere"  # (de-jolie-eperviere)
        product._set_url()
        url2 = self.env['url.url'].search([('model_id', '=',
                "product.template,9"), ('redirect', '=', False)]
        ).url_key

        print "les url: %s %s " % (url1, url2)
        urlurl1 = self.env['url.url']._get_object(url1)

        urlurl2 = self.env['url.url']._get_object(url2)

        self.assertEqual(urlurl1, urlurl2)
