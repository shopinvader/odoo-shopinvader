This addon adds logic to payments, specifically concerning the sale orders.
It defines a callback on payment transactions, in order to confirm the cart
(making it a quotation) when the payment is done.
What's more, it adds a configuration on the payment provider to decide if,
when the payment is done, the quotation must stay a quotation or be confirmed
into a sale order.
