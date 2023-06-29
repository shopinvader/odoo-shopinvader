#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

DEFAULT_LANG = "en_US"

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


class AbstractUrl(models.AbstractModel):
    _name = "abstract.url"
    _description = "Abstract Url"
    _have_url = True

    url_ids = fields.One2many("url.url", "res_id")

    def _get_url_keywords(self):
        """This method return a list of keyword that will be concatenated
        with '-' to generate the url
        Ex: if you return ['foo', '42'] the url will be foo-42

        Note the self already include in the context the lang of the record
        """
        self.ensure_one()
        # TODO: IMO we should add the ID here by default
        # to make sure the URL is always unique
        # seb.beau: not sure, most of site do not have id in url
        # the url have an seo impact so it's better to only put meaning information
        # moreover for unicity you can put the default code of the product or ean13
        return [self.name]

    def _generate_url_key(self):
        self.ensure_one()
        return slugify("-".join(self._get_url_keywords()))

    def _get_redirect_urls(self, referential, lang):
        self.ensure_one()
        return self.url_ids.filtered(
            lambda s: (
                s.lang_id.code == lang and s.referential == referential and s.redirect
            )
        )

    def _get_main_url(self, referential, lang):
        self.ensure_one()
        return self.url_ids.filtered(
            lambda s: (
                s.lang_id.code == lang
                and s.referential == referential
                and not s.redirect
            )
        )

    @api.model
    def _prepare_url(self, referential, lang, url_key):
        return {
            "key": url_key,
            "redirect": False,
            "res_model": self._name,
            "res_id": self.id,
            "referential": referential,
            "lang_id": self.env["res.lang"]._lang_get_id(lang),
        }

    def _reuse_url(self, existing_url):
        # TODO add user notification in the futur SEO dashboard
        existing_url.write(
            {
                "res_model": self._name,
                "res_id": self.id,
                "redirect": False,
            }
        )

    def _update_url_key(self, referential="global", lang=DEFAULT_LANG):
        for record in self.with_context(lang=lang):
            # TODO maybe we should have a computed field that flag the
            # current url if the key used for building the url have changed
            # so we can skip this check if nothing have changed
            current_url = record._get_main_url(referential, lang)
            if not current_url.manual:
                url_key = record._generate_url_key()
                if current_url.key != url_key:
                    current_url.redirect = True
                    record._add_url(referential, lang, url_key)

    def _add_url(self, referential, lang, url_key):
        self.ensure_one()
        existing_url = self.env["url.url"].search(
            [
                ("referential", "=", referential),
                ("lang_id.code", "=", lang),
                ("key", "=", url_key),
            ]
        )
        if existing_url:
            if existing_url.redirect:
                self._reuse_url(existing_url)
            else:
                raise UserError(
                    _(
                        "Url_key already exist in other model"
                        "\n- name: %(model_name)s\n - id: %(model_id)s\n"
                        "- url_key: %(url_key)s\n - url_key_id %(url_id)s"
                    )
                    % dict(
                        model_name=existing_url.model_id.name,
                        model_id=existing_url.model_id.id,
                        url_key=existing_url.url_key,
                        url_id=existing_url.id,
                    )
                )

        else:
            vals = self._prepare_url(referential, lang, url_key)
            self.env["url.url"].create(vals)

    def _redirect_existing_url(self, action):
        """
        This method is called when the record is deactivated to give a chance
        to the concrete model to implement a redirect strategy
        action can be "archived" or "unlink"
        """
        return True

    def unlink(self):
        for record in self:
            record._redirect_existing_url("unlink")
            # Remove dead url that have been not redirected
            record.url_ids.unlink()
        return super().unlink()

    def write(self, vals):
        res = super().write(vals)
        if "active" in vals and not vals["active"]:
            self._redirect_existing_url("archived")
        return res
