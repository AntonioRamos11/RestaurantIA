from datetime import datetime, timedelta, date
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Text, create_engine, func, select, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker


app = FastAPI(title="RestaurantIA API", version="0.2.0")


# In-memory demo data (replace with Postgres + SQLAlchemy in M1)
TABLES = [
    {"id": 1, "capacity": 2},
    {"id": 2, "capacity": 2},
    {"id": 3, "capacity": 4},
    {"id": 4, "capacity": 4},
    {"id": 5, "capacity": 6},
]
RESERVATIONS: Dict[str, Dict] = {}

DEFAULT_DURATION_MIN = 90


class ReservationIn(BaseModel):
    when: datetime = Field(..., description="Reservation start time (ISO 8601)")
    party_size: int = Field(..., ge=1, le=12)
    customer_name: str
    phone: Optional[str] = None
    notes: Optional[str] = None


class ReservationOut(BaseModel):
    id: str
    when: datetime
    party_size: int
    table_id: Optional[int]
    status: str  # confirmed | waitlist | rejected


def _overlaps(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    return not (end1 <= start2 or end2 <= start1)


def _table_is_free(table_id: int, when: datetime, duration_min: int) -> bool:
    end = when + timedelta(minutes=duration_min)
    for r in RESERVATIONS.values():
        if r["table_id"] != table_id or r["status"] != "confirmed":
            continue
        r_start = r["when"]
        r_end = r_start + timedelta(minutes=r.get("duration_min", DEFAULT_DURATION_MIN))
        if _overlaps(r_start, r_end, when, end):
            return False
    return True


def _find_table(party_size: int, when: datetime, duration_min: int) -> Optional[int]:
    candidates = sorted([t for t in TABLES if t["capacity"] >= party_size], key=lambda t: t["capacity"])
    for t in candidates:
        if _table_is_free(t["id"], when, duration_min):
            return t["id"]
    return None


@app.get("/health")
def health():
    return {"ok": True, "service": "reservations"}


@app.get("/availability")
def availability(
    when: datetime = Query(..., description="ISO 8601 datetime"),
    party_size: int = Query(..., ge=1, le=12),
    duration_min: int = Query(DEFAULT_DURATION_MIN, ge=30, le=240),
):
    table_id = _find_table(party_size, when, duration_min)
    return {"available": table_id is not None, "table_id": table_id}


@app.post("/reservations", response_model=ReservationOut)
def create_reservation(res: ReservationIn, duration_min: int = DEFAULT_DURATION_MIN):
    table_id = _find_table(res.party_size, res.when, duration_min)
    status = "confirmed" if table_id else "waitlist"
    rid = f"r_{len(RESERVATIONS) + 1}"
    RESERVATIONS[rid] = {
        "id": rid,
        "when": res.when,
        "party_size": res.party_size,
        "table_id": table_id,
        "status": status,
        "customer_name": res.customer_name,
        "phone": res.phone,
        "notes": res.notes,
        "duration_min": duration_min,
    }
    return ReservationOut(id=rid, when=res.when, party_size=res.party_size, table_id=table_id, status=status)


@app.get("/reservations/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: str):
    r = RESERVATIONS.get(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return ReservationOut(id=r["id"], when=r["when"], party_size=r["party_size"], table_id=r["table_id"], status=r["status"])


# --- M0: Covers (daily/hourly) using SQLite + SQLAlchemy ---
DATABASE_URL = "sqlite:///./restaurantia.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=True)
    orders = relationship("Order", back_populates="location")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True, nullable=False)
    covers = Column(Integer, nullable=False, default=1)
    ts = Column(DateTime, index=True, nullable=False)

    location = relationship("Location", back_populates="orders")


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.id"), index=True, nullable=False)
    qty = Column(Integer, nullable=False, default=1)

    # Optional relationships
    # order = relationship("Order")
    # item = relationship("MenuItem")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True, nullable=False)
    ts = Column(DateTime, index=True, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 optional
    text = Column(Text, nullable=False)
    source = Column(String, nullable=True)  # e.g., google, onsite, delivery
    sentiment = Column(Float, nullable=True)  # compound score from VADER


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    unit = Column(String, nullable=False, default="unit")  # e.g., g, ml, unit


class RecipeItem(Base):
    __tablename__ = "recipe_items"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"), index=True, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), index=True, nullable=False)
    qty_per_serving = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('item_id', 'ingredient_id', name='uq_item_ingredient'),)


class InventoryLevel(Base):
    __tablename__ = "inventory_levels"
    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), index=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True, nullable=False)
    on_hand = Column(Float, nullable=False, default=0.0)
    __table_args__ = (UniqueConstraint('ingredient_id', 'location_id', name='uq_ingredient_location'),)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=False, index=True, nullable=True)
    marketing_consent = Column(Integer, nullable=False, default=0)  # 0/1
    analytics_consent = Column(Integer, nullable=False, default=1)  # 0/1
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"
    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, unique=True, index=True, nullable=False)  # e.g., 'orders','reviews','customers'
    days = Column(Integer, nullable=False)  # retain this many days


# --- Multi-tenant Onboarding Models ---
class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    timezone = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class ProvisionRun(Base):
    __tablename__ = "provision_runs"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending|running|completed|failed
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
    message = Column(Text, nullable=True)


class DiningTable(Base):
    __tablename__ = "dining_tables"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=False)
    location_id = Column(Integer, index=True, nullable=False)
    name = Column(String, nullable=True)
    capacity = Column(Integer, nullable=False, default=2)


def init_db():
    Base.metadata.create_all(bind=engine)
    # Ensure locations.tenant_id exists in SQLite (lightweight migration)
    with engine.connect() as conn:
        try:
            cols = [row[1] for row in conn.execute(func.printf("%s", "")).cursor]  # placeholder
        except Exception:
            cols = []
        try:
            res = conn.execute("PRAGMA table_info(locations)")
            col_names = [r[1] for r in res.fetchall()]
            if "tenant_id" not in col_names:
                conn.execute("ALTER TABLE locations ADD COLUMN tenant_id INTEGER")
        except Exception:
            pass


@app.on_event("startup")
def _startup():
    init_db()


class SeedRequest(BaseModel):
    days: int = Field(7, ge=1, le=60)
    locations: List[str] = Field(default_factory=lambda: ["Downtown", "Uptown"])


@app.post("/seed")
def seed_demo(req: SeedRequest):
    import random

    db = SessionLocal()
    try:
        # Ensure locations
        loc_map: Dict[str, int] = {}
        for name in req.locations:
            loc = db.query(Location).filter(Location.name == name).first()
            if not loc:
                loc = Location(name=name)
                db.add(loc)
                db.flush()
            loc_map[name] = loc.id

        # Ensure menu items
        default_menu = [
            ("Burger", "Main", 10.0),
            ("Fries", "Side", 4.0),
            ("Coke", "Drink", 2.0),
            ("Salad", "Starter", 6.0),
            ("Pasta", "Main", 11.0),
            ("Wine", "Drink", 8.0),
            ("Tiramisu", "Dessert", 6.0),
            ("Water", "Drink", 1.5),
            ("Chicken Grill", "Main", 12.0),
            ("Soup", "Starter", 5.0),
        ]
        item_map: Dict[str, int] = {}
        for n, c, p in default_menu:
            mi = db.query(MenuItem).filter(MenuItem.name == n).first()
            if not mi:
                mi = MenuItem(name=n, category=c, price=p)
                db.add(mi)
                db.flush()
            item_map[n] = mi.id

        # Ensure ingredients and basic recipes
        ingredients_spec = [
            ("Beef Patty", "unit"), ("Bun", "unit"), ("Lettuce", "g"), ("Tomato", "g"), ("Fries Potatoes", "g"),
            ("Coke Syrup", "ml"), ("Sparkling Water", "ml"), ("Pasta Noodles", "g"), ("Tomato Sauce", "ml"),
            ("Chicken Breast", "g"), ("Wine Bottle", "ml"), ("Mascarpone", "g"), ("Egg", "unit"), ("Sugar", "g"),
            ("Soup Base", "ml"), ("Water", "ml")
        ]
        ingr_map: Dict[str, int] = {}
        for name, unit in ingredients_spec:
            ing = db.query(Ingredient).filter(Ingredient.name == name).first()
            if not ing:
                ing = Ingredient(name=name, unit=unit)
                db.add(ing)
                db.flush()
            ingr_map[name] = ing.id

        recipe_defs = {
            "Burger": [("Beef Patty", 1), ("Bun", 1), ("Lettuce", 20), ("Tomato", 20)],
            "Fries": [("Fries Potatoes", 150)],
            "Coke": [("Coke Syrup", 50), ("Sparkling Water", 200)],
            "Salad": [("Lettuce", 80), ("Tomato", 50)],
            "Pasta": [("Pasta Noodles", 120), ("Tomato Sauce", 150)],
            "Wine": [("Wine Bottle", 150)],
            "Tiramisu": [("Mascarpone", 100), ("Egg", 1), ("Sugar", 20)],
            "Water": [("Water", 250)],
            "Chicken Grill": [("Chicken Breast", 180)],
            "Soup": [("Soup Base", 250)],
        }
        for item_name, comps in recipe_defs.items():
            item_id = item_map[item_name]
            for ing_name, qty in comps:
                ing_id = ingr_map[ing_name]
                exists = db.query(RecipeItem).filter(RecipeItem.item_id == item_id, RecipeItem.ingredient_id == ing_id).first()
                if not exists:
                    db.add(RecipeItem(item_id=item_id, ingredient_id=ing_id, qty_per_serving=qty))

        # Seed basic inventory levels per location
        for loc_name, loc_id in loc_map.items():
            for ing_name, ing_id in ingr_map.items():
                inv = db.query(InventoryLevel).filter(InventoryLevel.location_id == loc_id, InventoryLevel.ingredient_id == ing_id).first()
                if not inv:
                    db.add(InventoryLevel(location_id=loc_id, ingredient_id=ing_id, on_hand=10000))  # generous default

        # Generate orders for each day/hour
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        start = now - timedelta(days=req.days)
        hours = int((now - start).total_seconds() // 3600)

        for name, loc_id in loc_map.items():
            for h in range(hours):
                ts = start + timedelta(hours=h)
                dow = ts.weekday()
                hour = ts.hour
                # Simple pattern: more covers on Fri/Sat dinner
                base = 2
                if 11 <= hour <= 14:
                    base += 3  # lunch
                if 18 <= hour <= 21:
                    base += 6  # dinner
                if dow in (4, 5):
                    base += 4  # weekend uplift
                noise = random.randint(-2, 3)
                covers = max(0, base + noise)
                if covers == 0:
                    continue
                order = Order(location_id=loc_id, covers=covers, ts=ts)
                db.add(order)
                db.flush()
                # Build bundles by context
                bundle: Dict[str, int] = {}
                def add_item(k: str, q: int = 1):
                    bundle[k] = bundle.get(k, 0) + q

                if 11 <= hour <= 14:
                    # Lunch patterns
                    if random.random() < 0.6:
                        add_item("Burger"); add_item("Fries"); add_item("Coke")
                    else:
                        add_item("Pasta"); add_item("Water")
                    if random.random() < 0.2:
                        add_item("Salad")
                elif 18 <= hour <= 21:
                    # Dinner patterns
                    if random.random() < 0.6:
                        add_item("Pasta"); add_item("Wine")
                    else:
                        add_item("Chicken Grill"); add_item("Wine")
                    if random.random() < 0.35:
                        add_item("Tiramisu")
                else:
                    # Off-peak simple orders
                    add_item("Soup")
                    if random.random() < 0.5:
                        add_item("Water")

                # Scale items relative to covers
                scale = max(1, covers // max(1, len([k for k in bundle if k in ("Burger","Pasta","Chicken Grill")])))
                for item_name, qty in bundle.items():
                    item_id = item_map[item_name]
                    db.add(OrderItem(order_id=order.id, item_id=item_id, qty=max(1, qty * scale // 2)))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


class CoversQuery(BaseModel):
    start_date: date
    end_date: date
    location: Optional[str] = None


@app.get("/analytics/covers/daily")
def covers_daily(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        q = (
            db.query(
                func.date(Order.ts).label("day"),
                func.sum(Order.covers).label("covers"),
                Location.name.label("location"),
            )
            .join(Location, Location.id == Order.location_id)
            .filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)
        )
        if location:
            q = q.filter(Location.name == location)
        q = q.group_by("day", Location.name).order_by("day")
        rows = q.all()
        return [
            {"day": str(r.day), "covers": int(r.covers), "location": r.location}
            for r in rows
        ]
    finally:
        db.close()


# --- Onboarding API: Tenants, Locations, Provisioning ---
class TenantIn(BaseModel):
    name: str
    timezone: Optional[str] = None
    currency: Optional[str] = None


class TenantOut(BaseModel):
    id: int
    name: str
    timezone: Optional[str]
    currency: Optional[str]
    created_at: datetime


@app.post("/tenants", response_model=TenantOut)
def create_tenant(body: TenantIn):
    db = SessionLocal()
    try:
        # unique by name
        existing = db.query(Tenant).filter(Tenant.name == body.name).first()
        if existing:
            return TenantOut(id=existing.id, name=existing.name, timezone=existing.timezone, currency=existing.currency, created_at=existing.created_at)
        rec = Tenant(name=body.name, timezone=body.timezone, currency=body.currency)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return TenantOut(id=rec.id, name=rec.name, timezone=rec.timezone, currency=rec.currency, created_at=rec.created_at)
    finally:
        db.close()


class LocationIn(BaseModel):
    name: str
    timezone: Optional[str] = None
    tables: Optional[List[Dict]] = None  # [{"name":"T1","capacity":2}, ...]


@app.post("/tenants/{tenant_id}/locations")
def add_location(tenant_id: int, body: LocationIn):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).get(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        # location unique by (tenant_id, name) — we only have name unique globally in M0; keep simple
        loc = db.query(Location).filter(Location.name == body.name).first()
        if not loc:
            loc = Location(name=body.name, tenant_id=tenant_id)
            db.add(loc)
            db.flush()
        else:
            loc.tenant_id = loc.tenant_id or tenant_id

        # Create tables if provided
        if body.tables:
            for t in body.tables:
                try:
                    nm = t.get("name")
                    cap = int(t.get("capacity", 2))
                except Exception:
                    nm = None
                    cap = 2
                db.add(DiningTable(tenant_id=tenant_id, location_id=loc.id, name=nm, capacity=cap))
        db.commit()
        return {"ok": True, "location_id": loc.id}
    finally:
        db.close()


class ProvisionRequest(BaseModel):
    menu_template: Optional[str] = None
    menu_overrides: Optional[List[Dict]] = None
    inventory_init: Optional[List[Dict]] = None
    employees: Optional[List[Dict]] = None
    shift_templates: Optional[List[Dict]] = None
    channels: Optional[Dict] = None
    governance: Optional[Dict] = None


@app.post("/tenants/{tenant_id}/provision")
def provision_tenant(tenant_id: int, payload: ProvisionRequest | None = None):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).get(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        run = ProvisionRun(tenant_id=tenant_id, status="running", started_at=datetime.now())
        db.add(run)
        db.flush()
        # M0 stub: mark completed immediately; in M1+ orchestrate steps (menu, recipes, inventory, staff, policies)
        run.status = "completed"
        run.finished_at = datetime.now()
        run.message = "Provisioning stub completed (M0)."
        db.commit()
        return {"ok": True, "run_id": run.id, "status": run.status}
    finally:
        db.close()


@app.get("/tenants/{tenant_id}/provision/{run_id}/status")
def provision_status(tenant_id: int, run_id: int):
    db = SessionLocal()
    try:
        run = db.query(ProvisionRun).get(run_id)
        if not run or run.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Run not found")
        return {
            "run_id": run.id,
            "tenant_id": run.tenant_id,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "message": run.message,
        }
    finally:
        db.close()


# --- Privacy & Governance M0: Customers (consent), PII inventory, retention policies ---
class CustomerIn(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    marketing_consent: Optional[bool] = False
    analytics_consent: Optional[bool] = True


class CustomerOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    marketing_consent: bool
    analytics_consent: bool
    created_at: datetime


@app.post("/customers", response_model=CustomerOut)
def create_customer(c: CustomerIn):
    db = SessionLocal()
    try:
        rec = Customer(
            name=c.name,
            email=(c.email or None),
            phone=(c.phone or None),
            marketing_consent=1 if c.marketing_consent else 0,
            analytics_consent=1 if c.analytics_consent else 0,
            created_at=datetime.now(),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return CustomerOut(
            id=rec.id,
            name=rec.name,
            email=rec.email,
            phone=rec.phone,
            marketing_consent=bool(rec.marketing_consent),
            analytics_consent=bool(rec.analytics_consent),
            created_at=rec.created_at,
        )
    finally:
        db.close()


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int):
    db = SessionLocal()
    try:
        rec = db.query(Customer).get(customer_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerOut(
            id=rec.id,
            name=rec.name,
            email=rec.email,
            phone=rec.phone,
            marketing_consent=bool(rec.marketing_consent),
            analytics_consent=bool(rec.analytics_consent),
            created_at=rec.created_at,
        )
    finally:
        db.close()


class ConsentUpdate(BaseModel):
    marketing_consent: Optional[bool] = None
    analytics_consent: Optional[bool] = None


@app.patch("/customers/{customer_id}/consent")
def update_consent(customer_id: int, body: ConsentUpdate):
    db = SessionLocal()
    try:
        rec = db.query(Customer).get(customer_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Customer not found")
        if body.marketing_consent is not None:
            rec.marketing_consent = 1 if body.marketing_consent else 0
        if body.analytics_consent is not None:
            rec.analytics_consent = 1 if body.analytics_consent else 0
        db.commit()
        return {"ok": True}
    finally:
        db.close()


@app.get("/governance/pii_inventory")
def pii_inventory():
    # Static inventory for M0; later derive from ORM metadata with annotations
    return {
        "customers": {
            "table": "customers",
            "pii_fields": ["name", "email", "phone"],
            "consent_fields": ["marketing_consent", "analytics_consent"],
        },
        "reservations_payload": {
            "api": "/reservations",
            "pii_fields": ["customer_name", "phone"],
            "storage": "in-memory (M0)",
        },
        "reviews": {
            "table": "reviews",
            "pii_fields": ["text"],
            "notes": "Free-text may contain PII; consider redaction/anonymization in M1+",
        },
    }


class RetentionPolicyIn(BaseModel):
    entity: str  # 'orders' | 'reviews' | 'customers'
    days: int


@app.get("/governance/retention/policies")
def list_retention_policies():
    db = SessionLocal()
    try:
        rows = db.query(RetentionPolicy).order_by(RetentionPolicy.entity).all()
        return [{"entity": r.entity, "days": r.days} for r in rows]
    finally:
        db.close()


@app.post("/governance/retention/policies")
def upsert_retention_policy(body: RetentionPolicyIn):
    db = SessionLocal()
    try:
        rec = db.query(RetentionPolicy).filter(RetentionPolicy.entity == body.entity).first()
        if not rec:
            rec = RetentionPolicy(entity=body.entity, days=body.days)
            db.add(rec)
        else:
            rec.days = body.days
        db.commit()
        return {"ok": True, "entity": body.entity, "days": body.days}
    finally:
        db.close()


@app.post("/governance/retention/apply")
def apply_retention():
    db = SessionLocal()
    try:
        policies = db.query(RetentionPolicy).all()
        now_dt = datetime.now()
        summary = {}
        for p in policies:
            cutoff = now_dt - timedelta(days=p.days)
            if p.entity == 'reviews':
                del_count = db.query(Review).filter(Review.ts < cutoff).delete(synchronize_session=False)
                summary['reviews'] = int(del_count)
            elif p.entity == 'orders':
                # Find orders to delete
                old_ids = [oid for (oid,) in db.query(Order.id).filter(Order.ts < cutoff).all()]
                if old_ids:
                    db.query(OrderItem).filter(OrderItem.order_id.in_(old_ids)).delete(synchronize_session=False)
                    del_count = db.query(Order).filter(Order.id.in_(old_ids)).delete(synchronize_session=False)
                else:
                    del_count = 0
                summary['orders'] = int(del_count)
            elif p.entity == 'customers':
                del_count = db.query(Customer).filter(Customer.created_at < cutoff).delete(synchronize_session=False)
                summary['customers'] = int(del_count)
            else:
                summary[p.entity] = 0
        db.commit()
        return {"ok": True, "deleted": summary}
    finally:
        db.close()


# --- Core Analytics: metrics and freshness ---
@app.get("/analytics/core/metrics")
def core_metrics(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        order_q = db.query(Order).filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)
        if location:
            order_q = order_q.join(Location, Location.id == Order.location_id).filter(Location.name == location)
        total_orders = order_q.count()
        covers_sum = db.query(func.coalesce(func.sum(Order.covers), 0)).filter(Order.id.in_(order_q.with_entities(Order.id))).scalar() or 0

        # Distinct hourly buckets within filter
        hours_q = (
            db.query(func.strftime('%Y-%m-%d %H:00:00', Order.ts).label('hour'))
            .filter(Order.id.in_(order_q.with_entities(Order.id)))
            .group_by('hour')
        )
        hours_count = hours_q.count()

        # Items sold and revenue
        item_base = (
            db.query(OrderItem, MenuItem.price)
            .join(Order, Order.id == OrderItem.order_id)
            .join(MenuItem, MenuItem.id == OrderItem.item_id)
        )
        if location:
            item_base = item_base.join(Location, Location.id == Order.location_id).filter(Location.name == location)
        item_base = item_base.filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)

        items_sold = db.query(func.coalesce(func.sum(OrderItem.qty), 0)).select_from(item_base.subquery()).scalar() or 0

        revenue_q = db.query(func.coalesce(func.sum(OrderItem.qty * func.coalesce(MenuItem.price, 0.0)), 0.0))\
            .join(Order, Order.id == OrderItem.order_id)\
            .join(MenuItem, MenuItem.id == OrderItem.item_id)
        if location:
            revenue_q = revenue_q.join(Location, Location.id == Order.location_id).filter(Location.name == location)
        revenue = float(
            revenue_q.filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end).scalar() or 0.0
        )

        avg_covers_per_hour = (covers_sum / hours_count) if hours_count else None
        avg_check_per_cover = (revenue / covers_sum) if covers_sum else None

        return {
            "total_orders": total_orders,
            "covers": int(covers_sum),
            "hours": hours_count,
            "avg_covers_per_hour": round(avg_covers_per_hour, 3) if avg_covers_per_hour is not None else None,
            "items_sold": int(items_sold),
            "revenue": round(revenue, 2),
            "avg_check_per_cover": round(avg_check_per_cover, 2) if avg_check_per_cover is not None else None,
        }
    finally:
        db.close()


@app.get("/analytics/core/freshness")
def core_freshness():
    db = SessionLocal()
    try:
        now_dt = datetime.now()
        def freshness_for(model, ts_col):
            max_ts = db.query(func.max(ts_col)).scalar()
            if not max_ts:
                return {"max_ts": None, "age_minutes": None, "status": "no-data"}
            age_min = (now_dt - max_ts).total_seconds() / 60.0
            status = "ok" if age_min <= 1440 else "stale"  # 24h SLO
            return {"max_ts": max_ts.isoformat(), "age_minutes": round(age_min, 1), "status": status}

        orders = freshness_for(Order, Order.ts)
        reviews = freshness_for(Review, Review.ts)
        return {"orders": orders, "reviews": reviews}
    finally:
        db.close()


# --- CSV Exports ---
@app.get("/exports/daily_covers.csv")
def export_daily_covers(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    rows = covers_daily(start=start, end=end, location=location)
    # rows as list of dicts with keys: day, covers, location
    lines = ["day,location,covers"] + [f"{r['day']},{r['location']},{r['covers']}" for r in rows]
    csv_text = "\n".join(lines) + "\n"
    return Response(content=csv_text, media_type="text/csv")


@app.get("/exports/item_sales.csv")
def export_item_sales(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        q = (
            db.query(
                func.date(Order.ts).label("day"),
                MenuItem.name.label("item"),
                func.sum(OrderItem.qty).label("qty"),
                func.sum(OrderItem.qty * func.coalesce(MenuItem.price, 0.0)).label("revenue"),
                Location.name.label("location"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .join(MenuItem, MenuItem.id == OrderItem.item_id)
            .join(Location, Location.id == Order.location_id)
            .filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)
        )
        if location:
            q = q.filter(Location.name == location)
        q = q.group_by("day", MenuItem.name, Location.name).order_by("day", MenuItem.name)
        rows = q.all()
        header = "day,location,item,qty,revenue"
        lines = [header]
        for r in rows:
            lines.append(f"{r.day},{r.location},{r.item},{int(r.qty)},{round(float(r.revenue or 0.0),2)}")
        csv_text = "\n".join(lines) + "\n"
        return Response(content=csv_text, media_type="text/csv")
    finally:
        db.close()


# --- M0: Inventory usage and on-hand tracking ---
class IngredientOut(BaseModel):
    id: int
    name: str
    unit: str


@app.get("/inventory/ingredients", response_model=List[IngredientOut])
def list_ingredients():
    db = SessionLocal()
    try:
        rows = db.query(Ingredient).order_by(Ingredient.name).all()
        return [IngredientOut(id=r.id, name=r.name, unit=r.unit) for r in rows]
    finally:
        db.close()


@app.get("/inventory/onhand")
def inventory_onhand(location: Optional[str] = Query(None)):
    db = SessionLocal()
    try:
        q = (
            db.query(
                Ingredient.name.label("ingredient"),
                Ingredient.unit.label("unit"),
                Location.name.label("location"),
                InventoryLevel.on_hand.label("on_hand"),
            )
            .join(InventoryLevel, InventoryLevel.ingredient_id == Ingredient.id)
            .join(Location, Location.id == InventoryLevel.location_id)
        )
        if location:
            q = q.filter(Location.name == location)
        rows = q.all()
        return [
            {"ingredient": r.ingredient, "unit": r.unit, "location": r.location, "on_hand": float(r.on_hand)}
            for r in rows
        ]
    finally:
        db.close()


class InventoryUpdateIn(BaseModel):
    ingredient: str
    location: str
    delta: float  # positive to add stock, negative to consume/adjust


@app.post("/inventory/adjust")
def inventory_adjust(body: InventoryUpdateIn):
    db = SessionLocal()
    try:
        loc = db.query(Location).filter(Location.name == body.location).first()
        if not loc:
            raise HTTPException(status_code=404, detail="Location not found")
        ing = db.query(Ingredient).filter(Ingredient.name == body.ingredient).first()
        if not ing:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        inv = db.query(InventoryLevel).filter(InventoryLevel.location_id == loc.id, InventoryLevel.ingredient_id == ing.id).first()
        if not inv:
            inv = InventoryLevel(location_id=loc.id, ingredient_id=ing.id, on_hand=0.0)
            db.add(inv)
            db.flush()
        inv.on_hand = max(0.0, float(inv.on_hand) + float(body.delta))
        db.commit()
        return {"ok": True, "ingredient": body.ingredient, "location": body.location, "on_hand": float(inv.on_hand)}
    finally:
        db.close()


@app.get("/inventory/usage")
def inventory_usage(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        # Select orders in window (and location if given)
        ord_q = db.query(Order.id, Order.location_id).filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)
        if location:
            ord_q = ord_q.join(Location, Location.id == Order.location_id).filter(Location.name == location)
        order_ids = [oid for (oid, _loc) in ord_q.all()]
        if not order_ids:
            return []

        # Join order items -> recipe -> aggregate ingredient usage
        q = (
            db.query(
                Ingredient.name.label("ingredient"),
                Ingredient.unit.label("unit"),
                func.sum(OrderItem.qty * RecipeItem.qty_per_serving).label("used"),
            )
            .join(RecipeItem, RecipeItem.item_id == OrderItem.item_id)
            .join(Ingredient, Ingredient.id == RecipeItem.ingredient_id)
            .filter(OrderItem.order_id.in_(order_ids))
            .group_by(Ingredient.name, Ingredient.unit)
            .order_by(func.sum(OrderItem.qty * RecipeItem.qty_per_serving).desc())
        )
        rows = q.all()
        return [
            {"ingredient": r.ingredient, "unit": r.unit, "used": float(r.used)}
            for r in rows
        ]
    finally:
        db.close()


# --- M0: Reviews NLP (Sentiment + Keywords) ---
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    _SIA_AVAILABLE = True
except Exception:
    _SIA_AVAILABLE = False


def _get_sia():
    if not _SIA_AVAILABLE:
        raise HTTPException(status_code=500, detail="NLTK/VADER not installed. Please install and download 'vader_lexicon'.")
    try:
        # Ensure lexicon present
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        # Attempt to download at runtime (best effort)
        try:
            nltk.download('vader_lexicon')
        except Exception:
            pass
    return SentimentIntensityAnalyzer()


def _simple_keywords(text: str, top_k: int = 10) -> List[str]:
    import re
    tokens = re.findall(r"[A-Za-zÀ-ÿ']+", text.lower())
    stop = set([
        'the','a','an','and','or','but','to','of','in','on','for','with','is','are','was','were','it','this','that','i','we','you','they','he','she','at','as','by','from','be','been','have','has','had','very','so','too','not','no','yes','my','our','their','your'
    ])
    freq: Dict[str, int] = {}
    for t in tokens:
        if t in stop or len(t) <= 2:
            continue
        freq[t] = freq.get(t, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:top_k]]


class ReviewIn(BaseModel):
    location: str
    ts: datetime
    rating: Optional[int] = None
    text: str
    source: Optional[str] = None


@app.post("/reviews")
def add_review(r: ReviewIn):
    db = SessionLocal()
    try:
        # get or create location
        loc = db.query(Location).filter(Location.name == r.location).first()
        if not loc:
            loc = Location(name=r.location)
            db.add(loc)
            db.flush()
        sentiment = None
        try:
            sia = _get_sia()
            sentiment = float(sia.polarity_scores(r.text).get('compound', 0.0))
        except Exception:
            sentiment = None
        rec = Review(location_id=loc.id, ts=r.ts, rating=r.rating, text=r.text, source=r.source, sentiment=sentiment)
        db.add(rec)
        db.commit()
        return {"ok": True, "id": rec.id, "sentiment": sentiment}
    finally:
        db.close()


@app.get("/reviews/summary")
def reviews_summary(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        q = db.query(Review, Location).join(Location, Location.id == Review.location_id).\
            filter(func.date(Review.ts) >= start, func.date(Review.ts) <= end)
        if location:
            q = q.filter(Location.name == location)
        rows = q.all()
        count = len(rows)
        if count == 0:
            return {"count": 0, "avg_rating": None, "avg_sentiment": None, "top_keywords": []}
        ratings = [rv.Review.rating for rv in rows if rv.Review.rating is not None]
        sentiments = [rv.Review.sentiment for rv in rows if rv.Review.sentiment is not None]
        texts = "\n".join([rv.Review.text for rv in rows])
        top_keywords = _simple_keywords(texts, top_k=15)
        return {
            "count": count,
            "avg_rating": round(sum(ratings) / len(ratings), 3) if ratings else None,
            "avg_sentiment": round(sum(sentiments) / len(sentiments), 4) if sentiments else None,
            "top_keywords": top_keywords,
        }
    finally:
        db.close()


# --- M0: Popularity and Co-occurrence Recommendations ---
class MenuItemOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    price: Optional[float] = None


@app.get("/menu/items", response_model=List[MenuItemOut])
def list_menu_items():
    db = SessionLocal()
    try:
        rows = db.query(MenuItem).order_by(MenuItem.name).all()
        return [MenuItemOut(id=r.id, name=r.name, category=r.category, price=r.price) for r in rows]
    finally:
        db.close()


@app.get("/recs/popular")
def recs_popular(
    start: Optional[date] = Query(None, description="YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
    top_k: int = Query(10, ge=1, le=100),
):
    db = SessionLocal()
    try:
        q = (
            db.query(
                MenuItem.id.label("item_id"),
                MenuItem.name.label("name"),
                func.sum(OrderItem.qty).label("qty"),
            )
            .join(MenuItem, MenuItem.id == OrderItem.item_id)
            .join(Order, Order.id == OrderItem.order_id)
            .join(Location, Location.id == Order.location_id)
        )
        if start:
            q = q.filter(func.date(Order.ts) >= start)
        if end:
            q = q.filter(func.date(Order.ts) <= end)
        if location:
            q = q.filter(Location.name == location)
        q = q.group_by(MenuItem.id, MenuItem.name).order_by(func.sum(OrderItem.qty).desc()).limit(top_k)
        rows = q.all()
        return [
            {"item_id": r.item_id, "name": r.name, "total_qty": int(r.qty)}
            for r in rows
        ]
    finally:
        db.close()


@app.get("/recs/cooccurrence")
def recs_cooccurrence(
    anchor_item_id: int = Query(..., ge=1),
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    location: Optional[str] = Query(None),
    top_k: int = Query(10, ge=1, le=100),
):
    db = SessionLocal()
    try:
        # Orders containing the anchor
        anchor_orders_q = (
            db.query(OrderItem.order_id)
            .join(Order, Order.id == OrderItem.order_id)
            .join(Location, Location.id == Order.location_id)
            .filter(OrderItem.item_id == anchor_item_id)
        )
        if start:
            anchor_orders_q = anchor_orders_q.filter(func.date(Order.ts) >= start)
        if end:
            anchor_orders_q = anchor_orders_q.filter(func.date(Order.ts) <= end)
        if location:
            anchor_orders_q = anchor_orders_q.filter(Location.name == location)
        anchor_order_ids = [oid for (oid,) in anchor_orders_q.distinct().all()]
        total_anchor_orders = len(anchor_order_ids)
        if total_anchor_orders == 0:
            return []

        # Count co-occurring items
        q = (
            db.query(
                OrderItem.item_id.label("item_id"),
                MenuItem.name.label("name"),
                func.count(func.distinct(OrderItem.order_id)).label("co_orders"),
            )
            .join(MenuItem, MenuItem.id == OrderItem.item_id)
            .filter(OrderItem.order_id.in_(anchor_order_ids))
            .filter(OrderItem.item_id != anchor_item_id)
            .group_by(OrderItem.item_id, MenuItem.name)
            .order_by(func.count(func.distinct(OrderItem.order_id)).desc())
            .limit(top_k)
        )
        rows = q.all()
        results = []
        for r in rows:
            attach_rate = r.co_orders / total_anchor_orders
            results.append({
                "item_id": r.item_id,
                "name": r.name,
                "co_orders": int(r.co_orders),
                "attach_rate": round(attach_rate, 4),
                "base_orders": total_anchor_orders,
            })
        return results
    finally:
        db.close()


@app.get("/analytics/covers/hourly")
def covers_hourly(
    start: date = Query(..., description="YYYY-MM-DD"),
    end: date = Query(..., description="YYYY-MM-DD"),
    location: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        q = (
            db.query(
                func.strftime('%Y-%m-%d %H:00:00', Order.ts).label("hour"),
                func.sum(Order.covers).label("covers"),
                Location.name.label("location"),
            )
            .join(Location, Location.id == Order.location_id)
            .filter(func.date(Order.ts) >= start, func.date(Order.ts) <= end)
        )
        if location:
            q = q.filter(Location.name == location)
        q = q.group_by("hour", Location.name).order_by("hour")
        rows = q.all()
        return [
            {"hour": r.hour, "covers": int(r.covers), "location": r.location}
            for r in rows
        ]
    finally:
        db.close()
