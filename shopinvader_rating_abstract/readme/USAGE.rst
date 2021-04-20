If you want to create a new module using this abstract all you need to is to copy this in your service file:

  class YourRatingService(Component):
      | _inherit = "shopinvader.abstract.rating.service"
      | _name = "your.service.name"
      | _usage = "your.usage"
      | _description = "your service description"
      | _rating_model = The model you want to add ratings to

You can also take a look at the shopinvader_rating_product module to see a concrete implementation.

If you want to use the notifications you don't need to implement anything, go to the `Notifications` tab in Shopinvader
and you will see two new notifications:

- New rating created for {the name of the rating_model's table}
- Publisher responded to a rating for {the name of the rating_model's table}
