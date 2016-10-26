# -*- coding: utf-8 -*-

from openerp import  api
from openerp.tests.common import SingleTransactionCase
from openerp.exceptions import Warning as UserError

class TestBaseUrl(SingleTransactionCase):

    
    def setup(self):
        super (TestBaseUrl,self).setup()

      
#    def test_product_name(self):

#       self.product = self.env['product.template'].browse(52)
#        toto = self.product

#        self.assertEqual('Advance', toto.name)
    
    def test_change_name(self):
        product = self.env['product.template'].browse(52)
        product.name = u"Un Joli épervier"  
             
        product.on_name_change()

       # import pdb; pdb.set_trace() 
        product._set_url()

        
        url_key = self.env['url.url'].search([('model_id','=', "product.template,52"),('redirect','=',False)]).url_key
        print (u"url_key : %s ", url_key)
        
        self.assertEqual('un-joli-epervier',url_key)
        
    def test_change_url_key(self):
        product = self.env['product.template'].browse(52)

        product.url_key = u"Un Joli épervier"  
        product._set_url()
        
        url_key = self.env['url.url'].search([('model_id','=', "product.template,52"),('redirect','=',False)]).url_key
        print (u"url_key : %s ", url_key)
        
        self.assertEqual('un-joli-epervier',url_key)
        
    def test_get_object(self):
        product = self.env['product.template'].browse(52)
        product.name = u"Un Joli épervier"  
             
        product.on_name_change()

        
        product._set_url()
        url1 = self.env['url.url'].search([('model_id','=', "product.template,52"),('redirect','=',False)]).url_key
        
        product.url_key = u"De Jolie éperviere" #(de-jolie-eperviere)  
        product._set_url()
        url2 = self.env['url.url'].search([('model_id','=', "product.template,52"),('redirect','=',False)]).url_key
        

        print "les url: %s %s " %(url1, url2)
        
        urlurl1 = self.env['url.url']._get_object(url1)
        
        urlurl2 = self.env['url.url']._get_object(url2)
        
        for i in urlurl2 : 
                self.assertTrue( i.model_id in urlurl1)
        
        import pdb; pdb.set_trace()         
        self.assertEqual(urlurl1 , urlurl2)
        
  
