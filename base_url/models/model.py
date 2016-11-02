# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import logging
from openerp.exceptions import Warning as UserError
_logger = logging.getLogger(__name__)
try:
    from slugify import slugify
except ImportError:
    _logger.debug('Cannot `import slugify`.')


class UrlUrl(models.Model):

    _name = "url.url"

    url_key = fields.Char(string="Url Id", store=True)
    model_id = fields.Reference(selection='_reference_models',
                                help="The id of product or category.",
                                readonly=True,
                                )
    redirect = fields.Boolean('Redirect')

    _sql_constraints = [("urlurl unique key",
                         'unique(url_key)',
                         'Already exists in database')]

    @api.model
    def _reference_models(self):
        return []

    @api.multi
    def _get_object(self, urls):
        """
        :return: return object attach to the url
        """
        object = self.search([("url_key", "=", urls)]).model_id
        return object


class AbstractUrl(models.AbstractModel):
    _name = "abstract.url"

    url_key = fields.Char(compute="_compute_url",
                          inverse="_inverse_set_url", string="Url key")
    redirect_url_key_ids = fields.One2many(compute="_compute_redirect_url",
                                           comodel_name="url.url")

    def _prepare_url(self, name=None):
        url_key = "prepare"
        if name is None:
            url_to_normalize = self.url_key
            url_key = slugify(url_to_normalize)
        else:
            url_to_normalize = name
            url_key = slugify(url_to_normalize)
        return url_key

    @api.multi
    def _inverse_set_url(self, name=None):
        """
        backup old url

        1 find url redirect true and same model_id
        if other model id refuse
        2 if exists set to False

        3 write the new one
        """

        model_ref = "%s,%s" % (self._name, self.id)
        url_key = ""
        if not name:
            url_key = self._prepare_url(name)
        else:
            url_key = self._prepare_url()

        other_models_url = self.env['url.url'].search(
            [('url_key', '=', url_key)]).model_id

        if other_models_url:
            for model in other_models_url:
                model_txt = "%s,%s" % (model._name, model.id)
                if model_txt != model_ref:
                    raise UserError(
                        _("Url_key already exist in other model"
                          " %s" % (other_models_url)))

        # existe elle .?
        search_url = self.env['url.url'].search([
            ('model_id', '=', model_ref),
            ('redirect', '=', False)])
        if search_url is False:
            _logger.info("NO url in place ", )
        for res in search_url:
            _logger.info("url in place: %s ", res)

        url_id = 0
        if search_url.url_key == url_key:
            url_id = search_url.id

        else:
            for url in self.redirect_url_key_ids:
                if url.url_key == url_key:
                    # update
                    search_url.redirect = True
                    url.redirect = False
                    url_id = url.id

        if url_id == 0:
            search_url.redirect = True
            Data = {'url_key': url_key,
                    'model_id': model_ref,
                    'redirect': False}
            self.env['url.url'].create(Data)

    @api.multi
    def _compute_url(self):

        model_ref = "%s,%s" % (self._name, self.id)
        _logger.info("used model  : %s ", model_ref)
        # import pdb; pdb.set_trace()
        url = self.env["url.url"].search([('model_id', '=', model_ref),
                                          ('redirect', '=', False)])
        if url:
            self.url_key = url[0].url_key

    @api.multi
    def _compute_redirect_url(self):
        """
        :return:

        """
        model_ref = "%s,%s" % (self._name, self.id)

        _logger.info("reference model : %s ", model_ref)

        self.redirect_url_key_ids = self.env["url.url"]\
            .search([('model_id', '=', model_ref), ('redirect', '=', True)])

    @api.onchange('name')
    def on_name_change(self):

        for record in self:
            name = record.name
            url_key = record._prepare_url(name)

            record.url_key = url_key
            # _logger.info("Output..: %s ", url_key )

    @api.onchange('url_key')
    def on_url_key_change(self):
        url = self._prepare_url(self.url_key)
        if url != self.url_key:
            raise UserError(_("it will will be adapted to %s" % (url)))
