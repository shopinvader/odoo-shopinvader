* Customer validation limitation

Customer validation is global: enable/disable affects all websites, if you have more than one.

Technical
~~~~~~~~~

* Create methods should be rewritten to support multi
*  The logic to bind / unbind products and categories should be implemented as
   component in place of wizard.
   Previously it was possible to work with in-memory record of the wizard to
   call the same logic from within odoo. In Odoo 13 it's no more the case.
   That means that to rebind thousand of records we must create thousand of
   rows into the database to reuse the logic provided by the wizard.
*  On product.category the name is no more translatable in V13.
   This functionality has been restored into shopinvader.
   This should be moved into a dedicated addon
