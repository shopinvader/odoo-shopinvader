While navigating on a company that has a main Shopinvader Backend configured,
go to any Product form and publish or unpublish it directly using the following
field.

.. image:: ../static/description/product_form.png

Technical note
~~~~~~~~~~~~~~

The binding is created immediately only if the flag is set from the template form.
If you are creating records programmaticaly (eg: imports)
and you set the flag the work will be delegated to a job.
