# Acme Pay Webhooks

Acme Pay sends webhook events to your server when something happens to a payment, for example payment.succeeded, payment.failed and refund.created. Configure the endpoint URL in the dashboard under Developers, then Webhooks.

Every webhook request includes a signature in the Acme-Signature header. Verify the signature using your webhook signing secret before trusting the payload. Compute an HMAC with SHA-256 over the raw request body and compare it with the signature using a constant-time comparison. Reject any event whose timestamp is more than five minutes old to prevent replay attacks.

Your endpoint must return a 2xx status code within ten seconds. If it does not, Acme Pay retries the delivery with exponential backoff: after 1 minute, 5 minutes, 30 minutes, 2 hours and 12 hours, for a maximum of five retries. After the final retry the event is marked as failed and can be resent manually from the dashboard.

Webhooks can be delivered more than once and out of order. Make your handler idempotent by storing the event id and ignoring ids you have already processed.
