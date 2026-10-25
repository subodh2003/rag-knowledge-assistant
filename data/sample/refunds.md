# Acme Pay Refunds and Disputes

You can refund a payment in full or in part through the API or the dashboard. Create a refund by sending a POST request to the refunds endpoint with the payment id and, for partial refunds, an amount in the smallest currency unit. A payment can be refunded multiple times as long as the total refunded does not exceed the original amount.

Refunds to cards usually appear on the customer statement within five to ten business days. Refunds are only possible for 180 days after the original payment; after that period you must pay the customer by other means. The processing fee on the original payment is not returned when you issue a refund.

When a customer disputes a charge with their bank, Acme Pay creates a dispute and notifies you by email and by the dispute.created webhook. You have seven days to submit evidence such as proof of delivery or the customer's signed receipt. If you lose a dispute, the disputed amount and a 15 dollar dispute fee are deducted from your next settlement.

Settlements are paid to your verified bank account every business day on a rolling two-day basis. For example, payments captured on Monday are settled on Wednesday.
