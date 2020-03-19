First of all you have to enable the feature:

Shopinvader backend -> Sale tab -> Enable "Validate customers"

Then the registration workflow changes as following:

* for each company binding a unique token is generated, you can see it in the Shopinvader tab on company form
* on Locomotive registration page users can enter the company token (if your theme does not support this yet, just add a text field named `company_token`)
* on odoo side, when the company token is given:

  * if the company is found, the new partner will be attached to the company with a specific type "Invader client user"
  * if the company is not found, the new partner will be created as a standalone customer as by default

* on Locomotive the main address will be the one of the company and not the one from the child partner.

NOTE: at the moment users on Locomotive side will be able to see all other address and they will be able to modify them, included the main one of the company.
