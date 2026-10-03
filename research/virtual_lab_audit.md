# Virtual-Lab Audit

Engineering fixture status: **PASS**.

Verified by `tests/test_lab.py`:

- authenticated narrow HTTP interface;
- no raw-oracle path in the public client;
- unavailable variants return `UNAVAILABLE` and consume no budget;
- duplicate assays consume no budget;
- exactly 24 successful assays per ordered round and 96 per run;
- restart-safe SQLite accounting and isolated run IDs;
- append-only private assay ledger;
- measured proposal source, model score, uncertainty, distance, and parent metadata are retained.

Real-data boundary status: **PASS**. The normalized 149,360-row oracle loaded behind the authenticated service, and the authenticated `/health` request passed on localhost. No assay was consumed and no fitness value was exposed during this smoke check. Budget semantics remain covered by the same service-path integration tests above.
