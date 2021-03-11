If UTM parameters are found in the HTTP header we are going to apply those parameters to the record only if the record inherits from utm.mixin (sale order, invoice, ...)

If you want to add another UTM parameter edit the *utm_params* dictionary in the controller by adding your desired UTM parameter like so:
  - "parameter": headers.get("HTTP_UTM_<PARAMETER>"),
