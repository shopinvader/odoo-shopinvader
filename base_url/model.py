# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from slugify import slugify
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
        :return: retourne l'objet liés à l'url
        """
        object = self.search([("url_key","=",urls)]).model_id
        return object

    # TODO faire une vue du model dans settings database structure URL ....


class AbstractUrl(models.AbstractModel):
    _name="abstract.url"

    url_key = fields.Char(compute="_compute_url", inverse="_set_url", string="Url key")
    redirect_url_key_ids = fields.One2many(compute="_compute_redirect_url",comodel_name="url.url")


    def _prepare_url(self):
        url_to_normalize = self.url_key
        url_key = slugify(url_to_normalize)
        return url_key

    @api.multi
    def _set_url(self, name=None):
        """
        sauvegarder ancienne url si exist et
        :return:
        1 rechercher une url avec redirect à true
        2 si elle existe passer à false
        3 ecrire nouvelle url modelid et true
        """

        model_ref = "%s,%s" % (self._name, self.id)

        search_txt = self.env["url.url"].search([('model_id' ,'=', model_ref),('redirect', '=', False)])
        if search_txt :
             search_txt.redirect = True;

        url_key = ""
        if name:
            self.url_key = name
            url_key = self._prepare_url()
        else:
            url_key = self._prepare_url()

        _logger.info("Quelle cle : %s ", url_key)

        Data= {'url_key' : url_key,
               'model_id' : model_ref,
               'redirect' : False}
        self.env['url.url'].create(Data)

    @api.multi
    def _compute_url(self):

        model_ref = "%s,%s" % (self._name, self.id)
        _logger.info ("model utilisee : %s ",model_ref)
        #import pdb; pdb.set_trace()
        url = self.env["url.url"].search([('model_id' ,'=', model_ref),('redirect', '=', False)])
        if url:
            self.url_key = url.url_key


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

        for record in self:
            #type = record.type
            name = record.name

            url_key = record.name
            _logger.info("sortie change..: %s ", url_key )
            record.url_key = url_key


"""
tester changement de nom produit : > nouvell url
tester regler une url manuellement (devient la bonne valeur)
verifier url redirection mise en oeuvre et ancienne url de produit fonctionnent encore

"""
