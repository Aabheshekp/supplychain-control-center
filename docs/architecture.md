# Architecture

FastAPI owns the REST contract and delegates persistence to a small SQLite service layer. SQLite transactions protect shipment state changes and inventory adjustments; every shipment status transition appends a history row. The static console uses the public API contract and has no framework build step.

```text
Browser console -> FastAPI routes -> service layer -> SQLite
                                  -> shipment event history
```

Demo mode seeds records on first startup. Set `SUPPLYCHAIN_DB` to a persistent volume path. The sample has no authentication: use an authenticated reverse proxy and restrict write routes before exposing it outside a trusted network.
