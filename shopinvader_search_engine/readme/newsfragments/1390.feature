A complete refactoring has been done to the code. This refactoring was driven by
the following goals:

* Make the code more readable and maintainable.
* Put in place a way to validate data exported to the indexes
* Ease the work of frontend developers by providing a schema for the data
  exported to the indexes.

Some technical choices have been made to achieve these goals:

* We removed the need to force the developer to define a specific binding model
  for each model that needs to be indexed.
* We defined serializers based on Pydantic models. This choice allows you to
  validate the data, generate the documentation and the schema of the data
  exported to the indexes. It also makes the serialization mechanism more
  explicit and easier to understand.
* We defined more fine-grained modules.

If you need to add additional information to the data exported to the indexes,
you only need to extends the Pydantic models by adding your additional fields
and extending the method initializing the model from an odoo record.
