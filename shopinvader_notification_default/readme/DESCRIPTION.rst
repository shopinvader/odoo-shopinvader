Default notification templates for Shopinvader.

Provides the following notification types and their email templates:

* cart_confirmation
* sale_confirmation
* invoice_open
* new_customer_welcome
* new_customer_welcome_not_validated
* customer_validated
* customer_updated
* address_created
* address_created_not_validated
* address_validated
* address_updated

Email templates are cooked using
`email_template_qweb <https://github.com/OCA/social/email_template_qweb>`_
and `mail_inline_css <https://github.com/OCA/social/mail_inline_css>`_,
hence you find:

* a common layout for all emails
* easy way to specify styles all at once (only in layout for now)
* easy way to override specific templates or part of them
