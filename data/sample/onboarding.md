# Acme Pay Integration Guide: Getting Started

To start integrating with Acme Pay, create a sandbox account from the developer dashboard. Sandbox accounts are free and never move real money. Each sandbox account is issued a pair of API keys: a publishable key that starts with pk_test and a secret key that starts with sk_test.

Keep the secret key on your server. Never embed it in a mobile app or in front-end JavaScript. If a secret key is exposed, rotate it immediately from the dashboard under Developers, then API Keys, then Roll key. The old key keeps working for 24 hours so you can deploy the new one without downtime.

Before going live you must complete business verification. Verification normally takes two to three business days and requires your company registration number, a bank account for settlements, and the identity of a company director. Live keys are only issued after verification is approved.

All requests must use HTTPS and be authenticated with the secret key sent as a bearer token in the Authorization header. Requests over plain HTTP are rejected with a 403 error.
