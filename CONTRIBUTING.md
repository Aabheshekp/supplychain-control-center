# Contributing

1. Keep shipment state transitions explicit and preserve the event history.
2. Use parameterized SQL and validate all new request models.
3. Update the OpenAPI behavior and browser console together when endpoints change.
4. Never commit operational shipment or inventory records.
5. Use a focused branch and describe the change and any deployment impact.

The CI workflow currently checks dependency installation and Python compilation.
