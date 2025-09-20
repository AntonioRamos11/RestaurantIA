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

## Automated Onboarding (Multi-tenant provisioning)

Objectives

- One-click provisioning per restaurant (tenant).
- Idempotent, repeatable setup from templates.
- Tenant isolation for data, auth, and analytics.

Core artifacts to provision

- Tenant and locations (timezone, address).
- Floor plan: tables, capacities, sections.
- Menu catalog: items, categories, prices, taxes.
- Recipes/BOM: ingredients, qty per serving, units.
- Inventory: on-hand levels, reorder points, suppliers.
- Employees: roles, pay rates, skills, schedules (shift templates).
- Channels/config: dine-in, delivery, POS/payment/accounting keys.
- Governance: consent defaults, retention policies, roles/permissions.

Architecture

- Multi-tenant: every table scoped by tenant_id (and location_id).
- Template library: cuisine/menu templates, floor plan templates, staffing templates, inventory starter packs.
- Provisioning flow: Prefect (or similar) orchestrated steps calling FastAPI endpoints; idempotent tasks with rollback.
- Admin UI: Streamlit tab “Onboarding” to trigger/monitor provisioning.

Provisioning flow (API-first)

- POST /tenants → create tenant
- POST /tenants/{tenant_id}/locations → add locations
- POST /tenants/{tenant_id}/provision → run end-to-end provisioning from templates
- GET /tenants/{tenant_id}/provision/{run_id}/status → logs/checks

Example provisioning payload

```json
{
	"tenant": {
		"name": "Ocean View Group",
		"timezone": "America/Los_Angeles",
		"currency": "USD"
	},
	"locations": [
		{
			"name": "Ocean View – Downtown",
			"timezone": "America/Los_Angeles",
			"floorplan_template": "small_60_seats",
			"tables": [
				{"name": "T1", "capacity": 2},
				{"name": "T2", "capacity": 4}
			]
		}
	],
	"menu_template": "italian_modern_v1",
	"menu_overrides": [
		{"item_name": "Truffle Fries", "price": 9.5},
		{"item_name": "House Pinot (glass)", "price": 12.0}
	],
	"recipes": [
		{"item_name": "Margherita Pizza", "ingredient": "Mozzarella", "unit": "g", "qty": 120},
		{"item_name": "Margherita Pizza", "ingredient": "Tomato Sauce", "unit": "g", "qty": 90}
	],
	"inventory_init": [
		{"ingredient": "Mozzarella", "on_hand": 20000, "reorder_point": 5000, "supplier": "DairyCo"},
		{"ingredient": "Tomato Sauce", "on_hand": 30000, "reorder_point": 6000, "supplier": "Saucy Ltd"}
	],
	"employees": [
		{"name": "Maria Rossi", "role": "Chef", "hourly_rate": 28, "skills": ["pizza", "pasta"]},
		{"name": "Alex Chen", "role": "Server", "hourly_rate": 16, "skills": ["wine"]}
	],
	"shift_templates": [
		{"role": "Server", "daypart": "dinner", "start": "17:00", "end": "22:00", "min_staff": 3}
	],
	"channels": {
		"dine_in": true,
		"delivery": ["UberEats", "DoorDash"],
		"pos": {"provider": "MockPOS", "api_key": "REDACTED"},
		"payments": {"provider": "Stripe", "account_id": "acct_..."}
	},
	"governance": {
		"default_consents": {"marketing": false, "analytics": true},
		"retention_days": {"orders": 730, "reviews": 365, "customers": 1095}
	}
}
```

Next steps in this repo

- Add models and migrations for tenant/location/table/employee/role/shift_template/supplier/tax_config.
- Create templates/ directory (YAML/JSON) for menu, floorplan, recipes, staffing, inventory.
- Implement /tenants, /locations, /provision endpoints and a Prefect flow to orchestrate steps.
- Add a Streamlit “Onboarding” tab to submit the provisioning payload and show step logs.
- Add smoke tests to validate a new tenant in CI (seed, validate, teardown).