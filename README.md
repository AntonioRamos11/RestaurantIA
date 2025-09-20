RestaurantIA
AI-first platform to run and optimize restaurants: forecasting demand, clustering tastes, explaining “reasons to visit,” personalizing menus and promos, and automating reservations, inventory, and staffing.

What’s here now
- A minimal FastAPI backend with an in-memory Reservations API (M0 of the roadmap).
- A Flet desktop UI prototype under `POO_restaurante/` for tables, orders, and menu.

Roadmap
See `roadmap.md` for a divide-and-conquer plan covering Reservations, Demand Forecasting, Recommendations, Reviews NLP, Inventory, Analytics, and Privacy.

Quickstart (Linux)
1) Create a virtualenv and install backend deps
	- python3 -m venv .venv
	- source .venv/bin/activate
	- pip install -r backend/requirements.txt
2) Run the API (reload for dev)
	- uvicorn backend.app.main:app --reload --port 8000
3) Optional: Run the Frontend Console (Streamlit UI)
	- In another terminal:
	  - cd frontend_streamlit
	  - python3 -m venv .venv && source .venv/bin/activate
	  - pip install -r requirements.txt
	  - streamlit run app.py
4) Try it
	- GET http://127.0.0.1:8000/health
	- GET http://127.0.0.1:8000/availability?when=2025-09-30T20:00:00&party_size=4
	- POST http://127.0.0.1:8000/reservations with JSON:
	  {"when": "2025-09-30T20:00:00", "party_size": 4, "customer_name": "Alex"}
	 - Seed demo data for analytics (7 days, 2 locations default):
		 POST http://127.0.0.1:8000/seed with JSON: {"days": 7}
	 - Covers analytics (M0):
		 GET http://127.0.0.1:8000/analytics/covers/daily?start=2025-09-01&end=2025-09-20
		 GET http://127.0.0.1:8000/analytics/covers/hourly?start=2025-09-15&end=2025-09-20

Next steps (Milestone M1)
- Replace in-memory storage with PostgreSQL + SQLAlchemy models and Alembic migrations.
- Add reservation conflict constraints and simple overbooking guard.
- Expose list/cancel endpoints; add basic auth and rate limiting.
- Connect analytics: utilization and no-show KPIs.

Frontend Console Tabs
- Health: set backend URL and ping /health
- Seed: generate demo orders/menu/inventory
- Reservations: check availability and create reservations
- Analytics: daily/hourly covers and core metrics
- Recommendations: popular items and co-occurrence
- Reviews: submit reviews and view sentiment/keywords summary
- Inventory: on-hand list, adjust stock, and usage by date range
- Customers & Governance: manage customers, consents, PII inventory, retention policies
- Exports: build CSV export links
- Onboarding: create tenant, add locations/tables, run provisioning and check status
