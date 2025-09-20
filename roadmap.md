# RestaurantIA Roadmap (Divide & Conquer)

Goal
Build a predictive, AI-first platform for restaurants: demand forecasting, taste clustering, reasons-to-visit insights, personalization, and operational optimization—delivered incrementally with clear milestones.

Guiding principles
- Deliver thin vertical slices that go end-to-end (data → model → API → dashboard).
- Favor simple baselines first, then iterate to smarter models.
- Instrument everything; define DoD with metrics and tests.
- Privacy-by-design: consent, minimization, and audit from day one.

Teams (streams)
- Core Data & Governance (CDG)
- Platform & API (PAPI)
- Intelligence & ML (IML)
- Analytics & Experimentation (ANX)
- Growth & Personalization (GRW)
- Operations Optimization (OPS)

Milestones by capability (maturity levels)
1) Reservations & Waitlist
- M0: In-memory API for /availability and /reservations (baseline).
- M1: Postgres models, constraints, table assignment, basic overbooking guard.
- M2: No-show probability model; waitlist automation; SMS/email notifications.
- M3: Real-time seat optimizer, table turn predictions, multi-location balancing.

2) Demand Forecasting (covers)
- M0: SQL daily/hourly aggregates per location.
- M1: Classical ML (Prophet/SARIMAX/LGBM) per location x daypart; MAPE < 20%.
- M2: Add weather/events; hierarchical reconciliation; MAPE < 12%.
- M3: Online updates, anomaly detection, auto-staffing/export.

3) Taste Graph & Recommendations
- M0: Co-occurrence + popularity baseline; attach-rate metric.
- M1: Item embeddings (sentence-transformers) + ingredient tags; segment clusters.
- M2: Context-aware recs (time, inventory, demand); next-best-offer.
- M3: Multi-objective recs (margin, waste, satisfaction) with constraints.

4) Reviews NLP (“reasons to visit”)
- M0: Sentiment + keywords.
- M1: BERTopic for themes; location- and segment-level themes.
- M2: Tie themes to menu/ops actions; monitor theme shift after changes.
- M3: Closed-loop attribution (themes → actions → uplift).

5) Inventory & Ops
- M0: Usage per recipe; basic on-hand tracking.
- M1: Inventory forecasting; stockout and waste KPIs.
- M2: Auto-replenishment suggestions; prep-level guidance by daypart.
- M3: Sustainability nudges and dynamic portion recommendations.

6) Analytics & Experimentation
- M0: dbt staging, Metabase/Superset dashboards; core metrics.
- M1: Marts for demand, menu, customers; source freshness SLOs.
- M2: A/B framework with CUPED; uplift modeling; guardrails.
- M3: Automated experiment assignment and results QA.

7) Privacy & Governance
- M0: Consent flags, PII inventory, data retention policy.
- M1: PII vaulting, access controls, audit logs.
- M2: Hashing/tokenization for joins; deletion workflows.
- M3: Differential privacy for analytics exports.

Phase plan (10 sprints, 2 weeks each)

Sprint 1: Foundation (CDG, PAPI, ANX)
- Repo scaffolding, FastAPI, Docker, pytest.
- Postgres + SQLAlchemy + Alembic; dbt project init.
- Health endpoint, logging, tracing; basic dashboards (orders/covers).
DoD: CI green, containers run locally, one dashboard loads.

Sprint 2: Reservations M1 (PAPI, CDG)
- Tables, Reservations models/migrations; constraints and indexes.
- CRUD + table assignment service; conflict tests.
- Seed data, Postman/pytest integration tests.
DoD: Book/search/cancel works; utilization metric visible.

Sprint 3: Demand M1 (IML, ANX)
- Aggregations (hourly/daily) in dbt; feature store tables.
- Train/evaluate baseline forecaster; backtest; MAPE reported.
- Forecast API + scheduled job (Prefect).
DoD: Forecasts visible in dashboard; alert on data gaps.

Sprint 4: Taste M1 (IML, GRW)
- Build item embeddings from names/ingredients; co-occurrence baseline.
- Segment customers by order vectors; top-N recs endpoint.
- “Attach rate” and “margin lift” tiles.
DoD: Recs API returns results <250ms p95; dashboards show lift.

Sprint 5: Reviews M1 (IML, ANX)
- Ingest reviews; sentiment + BERTopic; theme taxonomy.
- Theme dashboards per location; data quality checks.
DoD: Themes refresh nightly; top reasons-to-visit tracked.

Sprint 6: Reservations M2 (IML, PAPI)
- No-show model (logistic baseline); overbooking buffer rules.
- Waitlist automation; notification webhooks (stub).
DoD: No-show score in booking response; KPIs: no-show rate trend.

Sprint 7: Demand M2 (IML)
- Weather/events features; hierarchical reconciliation.
- Staff suggestion export; forecast error monitors.
DoD: MAPE < 12% on validation; staffing CSV delivered.

Sprint 8: Personalization M2 (GRW)
- Context-aware recs: include time, demand, inventory.
- Next-best-offer per user segment; campaign API.
DoD: Campaigns configurable; uplift experiment template ready.

Sprint 9: Inventory M2 (OPS)
- Forecast usage; reorder suggestions; waste KPIs.
- Prep-level guidance by daypart.
DoD: Stockout rate and waste dashboards trending.

Sprint 10: Experimentation M2 + Privacy M1 (ANX, CDG)
- A/B framework (assignment, logging, CUPED); results UI.
- PII vaulting, access roles, deletion workflow.
DoD: First experiment shipped; privacy checks automated in CI.

Workstream backlogs (epics → tasks)

Core Data & Governance
- Epics: Warehousing, dbt staging/marts, data quality, privacy.
- Tasks: Source models, tests, freshness SLOs, lineage, PII vault, deletion jobs.

Platform & API
- Epics: Auth, Reservations, Availability, Campaigns, Notifications.
- Tasks: Models/migrations, services, routers, rate limiting, observability.

Intelligence & ML
- Epics: Demand, No-show, Embeddings, Recs, Reviews, Inventory.
- Tasks: Feature engineering, training scripts, evaluation, model registry, batch/online scoring.

Analytics & Experimentation
- Epics: Dashboards, Metrics layer, A/B infra, Uplift modeling.
- Tasks: Semantic layer definitions, tiles, experiment store, CUPED, guardrails.

Growth & Personalization
- Epics: Segmentation, Offers, Triggering, CRM syncs.
- Tasks: Segment rules, next-best-offer API, channel webhooks, attribution.

Operations Optimization
- Epics: Staffing export, Prep guidance, Waste reduction.
- Tasks: Heuristics → ML, schedule generator, inventory interface.

Definition of Done (per feature)
- Code + tests + docs; observability (metrics/logs/traces).
- Data contracts and freshness tests.
- Security review and privacy checklist.
- Dashboard tile updated and linked to feature KPI.

KPIs (track per sprint)
- Forecast MAPE, seating utilization, wait time.
- No-show rate, table turn time.
- Attach rate, margin lift, personalization CTR.
- Waste reduction, stockout rate.
- Experiment impact (uplift, p-values, guardrail breaches).

Risks & mitigations
- Data quality: add great_expectations/dbt tests; alerts on failures.
- Cold-start recs: popularity fallback; explore-based campaigns.
- Model drift: scheduled backtests; retrain criteria.
- PII exposure: vaulting, role-based access, automated scans.

Immediate next actions
- S1: Stand up Postgres, Alembic, dbt; create Tables/Reservations; baseline dashboards.
- S2: Move reservations to Postgres, add conflict checks, integration tests.
- S3: Build demand v1 pipeline + API; add forecast tiles.
- S4: Ship embeddings + co-occurrence recs; measure attach rate.

Ownership map (example)
- CDG: Data models, dbt, privacy.
- PAPI: APIs, services, auth, infra.
- IML: Models, feature store, scoring.
- ANX: Dashboards, experiments.
- GRW: Offers, campaigns, CRM.
- OPS: Inventory, staffing.

Dependencies
- Recs depend on menu + orders.
- No-show depends on reservations history.
- Inventory forecasting depends on recipe usage + orders.
- Experimentation depends on analytics marts.

Environment & tooling
- Local: Docker Compose for API, DB, Metabase, Prefect, ML worker.
- CI: Linting, tests, dbt build/test, security scans.
- Release: Feature flags, canary deploys, migration guard.

Notes
- “r” = reservations: prioritized in Sprints 2 and 6.