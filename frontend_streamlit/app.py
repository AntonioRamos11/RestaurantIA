import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="RestaurantIA Console", layout="wide")

# Sidebar config
st.sidebar.title("Config")
backend_url = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:8000", key="cfg_backend_url")


def notify(msg: str, success: bool = True):
    if success:
        st.success(msg, icon="✅")
    else:
        st.error(msg, icon="❌")


# Tabs
TABS = [
    "Health", "Seed", "Reservations", "Analytics", "Recommendations",
    "Reviews", "Inventory", "Customers", "Exports"
]
selected = st.tabs(TABS)

# ---- Health ----
with selected[0]:
    st.header("Health")
    if st.button("Ping /health"):
        try:
            r = requests.get(backend_url.rstrip('/') + "/health", timeout=5)
            st.json(r.json())
        except Exception as ex:
            notify(f"Health check failed: {ex}", success=False)

# ---- Seed ----
with selected[1]:
    st.header("Seed demo data")
    c1, c2 = st.columns([1, 3])
    with c1:
        days = st.number_input("Days", min_value=1, max_value=60, value=7, key="seed_days")
    with c2:
        locs = st.text_input("Locations (comma-separated)", value="Downtown,Uptown", key="seed_locs")
    if st.button("Seed"):
        try:
            payload = {"days": int(days), "locations": [s.strip() for s in locs.split(',') if s.strip()]}
            r = requests.post(backend_url.rstrip('/') + "/seed", json=payload, timeout=30)
            r.raise_for_status()
            notify("Seed complete")
        except Exception as ex:
            notify(f"Seed failed: {ex}", success=False)

# Common date filter widget factory

def date_filters(prefix: str = ""):
    today = date.today()
    start = st.text_input(f"{prefix}Start (YYYY-MM-DD)", value=str(today.replace(day=max(1, today.day-7))), key=f"{prefix}start")
    end = st.text_input(f"{prefix}End (YYYY-MM-DD)", value=str(today), key=f"{prefix}end")
    location = st.text_input(f"{prefix}Location (optional)", value="", key=f"{prefix}location")
    return start, end, location

# ---- Reservations ----
with selected[2]:
    st.header("Reservations")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        when = st.text_input("When (ISO)", value=datetime.now().replace(microsecond=0).isoformat(), key="res_when")
    with c2:
        party = st.number_input("Party size", min_value=1, max_value=12, value=2, key="res_party")
    with c3:
        duration = st.number_input("Duration (min)", min_value=30, max_value=240, value=90, key="res_duration")
    c4, c5, c6 = st.columns([2,2,3])
    with c4:
        name = st.text_input("Customer name", value="Walk-in", key="res_name")
    with c5:
        phone = st.text_input("Phone", value="", key="res_phone")
    with c6:
        notes = st.text_input("Notes", value="", key="res_notes")
    c7, c8 = st.columns(2)
    if c7.button("Check availability"):
        try:
            params = {"when": when, "party_size": int(party), "duration_min": int(duration)}
            r = requests.get(backend_url.rstrip('/') + "/availability", params=params, timeout=10)
            st.json(r.json())
        except Exception as ex:
            notify(f"Availability error: {ex}", success=False)
    if c8.button("Create reservation"):
        try:
            payload = {"when": when, "party_size": int(party), "customer_name": name, "phone": phone or None, "notes": notes or None}
            r = requests.post(backend_url.rstrip('/') + f"/reservations?duration_min={int(duration)}", json=payload, timeout=10)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Reservation error: {ex}", success=False)

# ---- Analytics ----
with selected[3]:
    st.header("Analytics")
    st.subheader("Daily covers")
    s1, e1, loc = date_filters("Daily ")
    if st.button("Load daily covers"):
        try:
            params = {"start": s1, "end": e1}
            if loc: params["location"] = loc
            r = requests.get(backend_url.rstrip('/') + "/analytics/covers/daily", params=params, timeout=15)
            r.raise_for_status()
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Load daily failed: {ex}", success=False)
    st.subheader("Hourly covers")
    s2, e2, loc2 = date_filters("Hourly ")
    if st.button("Load hourly covers"):
        try:
            params = {"start": s2, "end": e2}
            if loc2: params["location"] = loc2
            r = requests.get(backend_url.rstrip('/') + "/analytics/covers/hourly", params=params, timeout=15)
            r.raise_for_status()
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Load hourly failed: {ex}", success=False)
    st.subheader("Core metrics")
    s3, e3, loc3 = date_filters("Metrics ")
    if st.button("Load core metrics"):
        try:
            params = {"start": s3, "end": e3}
            if loc3: params["location"] = loc3
            r = requests.get(backend_url.rstrip('/') + "/analytics/core/metrics", params=params, timeout=15)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Load metrics failed: {ex}", success=False)

# ---- Recommendations ----
with selected[4]:
    st.header("Recommendations")
    st.subheader("Popular items")
    topk = st.number_input("Top K", min_value=1, max_value=100, value=10, key="recs_topk")
    s4, e4, loc4 = date_filters("Popular ")
    if st.button("Load popular"):
        try:
            params = {"top_k": int(topk)}
            if s4: params["start"] = s4
            if e4: params["end"] = e4
            if loc4: params["location"] = loc4
            r = requests.get(backend_url.rstrip('/') + "/recs/popular", params=params, timeout=15)
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Popular failed: {ex}", success=False)
    st.subheader("Co-occurrence")
    try:
        items = requests.get(backend_url.rstrip('/') + "/menu/items", timeout=10).json()
    except Exception:
        items = []
    item_map = {f"{it['id']} - {it['name']}": it['id'] for it in items}
    anchor_label = st.selectbox("Anchor item", options=list(item_map.keys()) if item_map else ["—"], index=0, key="recs_anchor")
    s5, e5, loc5 = date_filters("Coocc ")
    if st.button("Load co-occurrence") and item_map:
        try:
            anchor_id = item_map.get(anchor_label)
            params = {"anchor_item_id": int(anchor_id), "top_k": int(topk)}
            if s5: params["start"] = s5
            if e5: params["end"] = e5
            if loc5: params["location"] = loc5
            r = requests.get(backend_url.rstrip('/') + "/recs/cooccurrence", params=params, timeout=15)
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Co-occurrence failed: {ex}", success=False)

# ---- Reviews ----
with selected[5]:
    st.header("Reviews")
    col1, col2, col3, col4 = st.columns([2,2,1,2])
    with col1:
        rv_loc = st.text_input("Location", value="Downtown", key="rv_location")
    with col2:
        rv_ts = st.text_input("Timestamp (ISO)", value=datetime.now().replace(microsecond=0).isoformat(), key="rv_ts")
    with col3:
        rv_rating = st.number_input("Rating (1-5)", min_value=1, max_value=5, value=5, key="rv_rating")
    with col4:
        rv_source = st.text_input("Source", value="onsite", key="rv_source")
    rv_text = st.text_area("Text", height=100, key="rv_text")
    if st.button("Submit review"):
        try:
            payload = {"location": rv_loc, "ts": rv_ts, "rating": int(rv_rating), "text": rv_text, "source": rv_source}
            r = requests.post(backend_url.rstrip('/') + "/reviews", json=payload, timeout=15)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Add review failed: {ex}", success=False)
    st.subheader("Summary")
    s6, e6, loc6 = date_filters("Review ")
    if st.button("Load summary"):
        try:
            params = {"start": s6, "end": e6}
            if loc6: params["location"] = loc6
            r = requests.get(backend_url.rstrip('/') + "/reviews/summary", params=params, timeout=15)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Summary failed: {ex}", success=False)

# ---- Inventory ----
with selected[6]:
    st.header("Inventory")
    inv_loc = st.text_input("Location (optional)", value="", key="inv_loc_opt")
    if st.button("Load on-hand"):
        try:
            params = {"location": inv_loc} if inv_loc else {}
            r = requests.get(backend_url.rstrip('/') + "/inventory/onhand", params=params, timeout=15)
            r.raise_for_status()
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Load on-hand failed: {ex}", success=False)
    st.subheader("Adjust")
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        ing = st.text_input("Ingredient", value="", key="inv_ing")
    with col2:
        inv_loc2 = st.text_input("Location", value="", key="inv_loc2")
    with col3:
        delta = st.number_input("Delta (+/-)", value=0.0, key="inv_delta")
    if st.button("Apply adjustment"):
        try:
            payload = {"ingredient": ing, "location": inv_loc2, "delta": float(delta)}
            r = requests.post(backend_url.rstrip('/') + "/inventory/adjust", json=payload, timeout=15)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Adjust failed: {ex}", success=False)
    st.subheader("Usage")
    s7, e7, loc7 = date_filters("Usage ")
    if st.button("Load usage"):
        try:
            params = {"start": s7, "end": e7}
            if loc7: params["location"] = loc7
            r = requests.get(backend_url.rstrip('/') + "/inventory/usage", params=params, timeout=15)
            r.raise_for_status()
            st.dataframe(pd.DataFrame(r.json()))
        except Exception as ex:
            notify(f"Usage failed: {ex}", success=False)

# ---- Customers / Governance ----
with selected[7]:
    st.header("Customers & Governance")
    st.subheader("Create customer")
    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
    with col1:
        c_name = st.text_input("Name", value="", key="cust_name")
    with col2:
        c_email = st.text_input("Email", value="", key="cust_email")
    with col3:
        c_phone = st.text_input("Phone", value="", key="cust_phone")
    with col4:
        c_m = st.toggle("Marketing", value=False, key="cust_marketing")
    with col5:
        c_a = st.toggle("Analytics", value=True, key="cust_analytics")
    if st.button("Create customer"):
        try:
            payload = {"name": c_name or None, "email": c_email or None, "phone": c_phone or None, "marketing_consent": bool(c_m), "analytics_consent": bool(c_a)}
            r = requests.post(backend_url.rstrip('/') + "/customers", json=payload, timeout=15)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Create customer failed: {ex}", success=False)
    st.subheader("Get / Update consent")
    col6, col7, col8, col9 = st.columns([1,1,1,2])
    with col6:
        cid = st.number_input("Customer ID", min_value=1, value=1, key="cust_id")
    with col7:
        u_m = st.toggle("Marketing", value=True, key="upd_marketing")
    with col8:
        u_a = st.toggle("Analytics", value=True, key="upd_analytics")
    if col9.button("Get"):
        try:
            r = requests.get(backend_url.rstrip('/') + f"/customers/{int(cid)}", timeout=10)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Get customer failed: {ex}", success=False)
    if col9.button("Update consent"):
        try:
            payload = {"marketing_consent": bool(u_m), "analytics_consent": bool(u_a)}
            r = requests.patch(backend_url.rstrip('/') + f"/customers/{int(cid)}/consent", json=payload, timeout=10)
            r.raise_for_status()
            st.json(r.json())
        except Exception as ex:
            notify(f"Update consent failed: {ex}", success=False)
    st.subheader("PII inventory")
    if st.button("Load PII inventory"):
        try:
            r = requests.get(backend_url.rstrip('/') + "/governance/pii_inventory", timeout=10)
            st.json(r.json())
        except Exception as ex:
            notify(f"PII inventory failed: {ex}", success=False)
    st.subheader("Retention policies")
    col10, col11 = st.columns([3,2])
    with col10:
        entity = st.text_input("Entity (orders|reviews|customers)", value="orders", key="ret_entity")
    with col11:
        days = st.number_input("Days", min_value=1, value=30, key="ret_days")
    c12, c13, c14 = st.columns([1,1,1])
    if c12.button("Save policy"):
        try:
            payload = {"entity": entity, "days": int(days)}
            r = requests.post(backend_url.rstrip('/') + "/governance/retention/policies", json=payload, timeout=10)
            r.raise_for_status()
            notify("Policy saved")
        except Exception as ex:
            notify(f"Save policy failed: {ex}", success=False)
    if c13.button("List policies"):
        try:
            r = requests.get(backend_url.rstrip('/') + "/governance/retention/policies", timeout=10)
            st.json(r.json())
        except Exception as ex:
            notify(f"List policies failed: {ex}", success=False)
    if c14.button("Apply retention"):
        try:
            r = requests.post(backend_url.rstrip('/') + "/governance/retention/apply", timeout=10)
            st.json(r.json())
        except Exception as ex:
            notify(f"Apply retention failed: {ex}", success=False)

# ---- Exports ----
with selected[8]:
    st.header("Exports")
    s8, e8, l8 = date_filters("Export ")
    if st.button("Build links"):
        params = f"start={s8}&end={e8}"
        if l8:
            params += f"&location={l8}"
        base = backend_url.rstrip('/')
        st.write(base + "/exports/daily_covers.csv?" + params)
        st.write(base + "/exports/item_sales.csv?" + params)
