This addon creates a custom redirect_form_html for custom providers.
This HTML contains the pending message defined on the custom provider plus
all the payment info.
It also allow to submit the form to redirect to a new route `/payment/providers/custom/pending`
where the transaction is set to pending and the callbacks are executed,
as in the standard Odoo flow.
