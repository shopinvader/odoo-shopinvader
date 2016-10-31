# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from slugify import slugify
from openerp.exceptions import Warning as UserError
import logging


_logger = logging.getLogger(__name__)

class UrlUrl(models.Model):

    _name= "url.url"

    url_key = fields.Char(string = "Url Id",store = True)
    model_id = fields.Reference(
                                selection='_reference_models',
                                help="The id of product or category.",
                                readonly=True,
                            )
    redirect = fields.Boolean('Redirect')
    
    @api.model
    def _reference_models(self):
        return []

    @api.multi
    def _get_object(self, urls):
        """
        :return: return object attach to the url
        """
        object = self.search([("url_key","=",urls)]).model_id
        return object

  
class AbstractUrl(models.AbstractModel):
    _name="abstract.url"

    url_key = fields.Char(compute="_compute_url", inverse="_set_url", string="Url key")
    redirect_url_key_ids = fields.One2many(compute="_compute_redirect_url",comodel_name="url.url")


    def _prepare_url(self, name = None):
        url_key = "prepare"
        if name == None :
            url_to_normalize= self.url_key
            url_key = slugify(url_to_normalize)
        else :
            url_to_normalize = name
            url_key = slugify(url_to_normalize)
        return url_key

    @api.multi
    def _set_url(self, name=None):
        """
        backup old url

        1 find url redirect true and same model_id
        if other model id refuse
        2 if exists set to False

        3 write the new one
        """

        model_ref = "%s,%s" % (self._name, self.id)
        url_key = ""
        if name != None :
            url_key = self._prepare_url(name)
        else:
            url_key = self._prepare_url()

            #existe elle .?

        _logger.info("la valeur to set: %s ", url_key)

        search_key = self.env['url.url'].search([('url_key', '=', url_key)])
        #Si url_key = self.url_key pas de changement..
        import pdb; pdb.set_trace()
        if not search_key :
            Data = {'url_key': url_key,
                    'model_id': model_ref,
                    'redirect': False}
            self.env['url.url'].create(Data)
        else:
            search_model = self.env['url.url'].browse(search_key.id).model_id
            url_key_list =self.env['url.url'].search([('model_id','=',model_ref)]).url_key
            _logger.info("listes url : %s",url_key_list)
            x = 0
            if len(search_key) < 2:
                model_key = "%s,%s" % (search_key.model_id._name, search_key.model_id.id)
                for key in url_key_list :
                    if key == self.url_key :
                        print "COUCOU ON EST L0"
                    #existe pour ce model search_key.redirect == False
                        search_key.redirect == True
                        x+1
                else :
                    #existe pour un autre modele_id
                    raise UserError(_(
                        "The generate url_key already exists for an other model %s" %(model_ref)
                    ))
            else:

                for key in search_key:
                    model_key = "%s,%s" % (key.model_id_name, key.model_id.id)
                    if model_key != model_ref and key.redirect == False :
                        # existe pour un autre modele_id et est active
                        raise UserError(_(
                            "The generate url_key already exists for an other model %s and is active" % (model_ref)
                        ))
                    elif model_key == model_ref :
                        key.redirect = False
                        x+1

            if x > 1 :
                raise UserError(_(
                    "The generate url_key already exists in too much state " % (model_ref)) )
            elif x < 1 :
                Data= {'url_key' : url_key,
                       'model_id' : model_ref,
                       'redirect' : False}
                self.env['url.url'].create(Data)


            # search_txt = self.env["url.url"].search([('model_id' ,'=', model_ref),('redirect', '=', False)])
            # if search_txt :
            #     search_txt.redirect = True;






    @api.multi
    def _compute_url(self):

        model_ref = "%s,%s" % (self._name, self.id)
        _logger.info ("model utilisee : %s ",model_ref)
        #import pdb; pdb.set_trace()
        url = self.env["url.url"].search([('model_id' ,'=', model_ref),('redirect', '=', False)])
        if url:
            self.url_key = url[0].url_key


    @api.multi
    def _compute_redirect_url(self):
        """
        :return:

        """
        model_ref = "%s,%s" % (self._name, self.id)

        _logger.info("model referencé : %s ", model_ref)

        self.redirect_url_key_ids = self.env["url.url"].search([('model_id', '=', model_ref), ('redirect', '=', True)])

    @api.onchange('name')
    def on_name_change(self):
        import pdb ; pdb.set_trace()
        for record in self:
            name = record.name
            url_key = record._prepare_url(name)
            record.url_key = url_key
            # _logger.info("sortie change..: %s ", url_key )



"""
tester changement de nom produit : > nouvell url
tester regler une url manuellement (devient la bonne valeur)
verifier url redirection mise en oeuvre et ancienne url de produit fonctionnent encore

"""
