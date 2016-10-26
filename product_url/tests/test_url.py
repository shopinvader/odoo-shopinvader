# -*- coding: utf-8 -*-

from openerp import  api
from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError

class TestBaseUrl(TransactionCase):

    
    def setup(self):
        super (TestBaseUrl,self).setup()

    
    def test_change_name(self):
        product = self.env['product.template'].browse(52)
        
        #
        
        product.name = u"Un Joli épervier"  
             
        product.on_name_change()

       # import pdb; pdb.set_trace() 
        product._set_url()

        
        url_key = self.env['url.url'].search([('model_id','=', "product.template,52"),('redirect','=',False)]).url_key
        print (u"url_key : %s ", url_key)
        
        self.assertEqual('un-joli-epervier',url_key)
        
    
    def test_product_name(self):

        self.product = self.env['product.template'].browse(52)
        toto = self.product

        self.assertEqual('Advance', toto.name)
