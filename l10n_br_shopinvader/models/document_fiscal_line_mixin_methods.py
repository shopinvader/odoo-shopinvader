# Copyright (C) 2023  Cristiano Rodrigues - Kmee <cristiano.rodrigues@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import models


class FiscalDocumentLineMixinMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"

    def _update_taxes(self):
        for line in self:
            if not line.fiscal_tax_ids:
                return self._onchange_product_id_fiscal()
            compute_result = self._compute_taxes(line.fiscal_tax_ids)
            computed_taxes = compute_result.get("taxes", {})
            line.amount_tax_included = compute_result.get("amount_included", 0.0)
            line.amount_tax_not_included = compute_result.get(
                "amount_not_included", 0.0
            )
            line.amount_tax_withholding = compute_result.get("amount_withholding", 0.0)
            line.estimate_tax = compute_result.get("estimate_tax", 0.0)
            for tax in line.fiscal_tax_ids:
                computed_tax = computed_taxes.get(tax.tax_domain, {})
                if hasattr(line, "%s_tax_id" % (tax.tax_domain,)):
                    # since v13, when line is a new record,
                    # line.fiscal_tax_ids recordset is made of
                    # NewId records with an origin pointing back to the original
                    # tax. tax.ids[0] is a way to the the single original tax back.
                    setattr(line, "%s_tax_id" % (tax.tax_domain,), tax.ids[0])
                    method = getattr(self, "_set_fields_%s" % (tax.tax_domain,))
                    if method:
                        method(computed_tax)
