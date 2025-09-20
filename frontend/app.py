import flet as ft
import requests
from datetime import datetime, date
from dateutil.parser import isoparse  # noqa: F401 (may be used later)

BACKEND_URL = "http://127.0.0.1:8000"


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def notify(page: ft.Page, text: str, ok: bool = True):
    page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=ft.Colors.GREEN_700 if ok else ft.Colors.RED_700)
    page.snack_bar.open = True
    page.update()


class RestaurantFrontend:
    def __init__(self, backend_url: str = BACKEND_URL):
        self.backend = backend_url.rstrip("/")

    # --------------- Tabs ---------------
    def view_health(self, page: ft.Page):
        health_text = ft.Text("—", size=14)
        url_field = ft.TextField(label="Backend URL", value=self.backend, width=400)

        def ping(_):
            try:
                self.backend = url_field.value.rstrip("/")
                r = requests.get(self.backend + "/health", timeout=5)
                health = r.json()
                health_text.value = str(health)
                page.update()
            except Exception as ex:
                notify(page, f"Health check failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Health & Config", size=20, weight=ft.FontWeight.BOLD),
            url_field,
            ft.Row([
                ft.ElevatedButton("Ping /health", on_click=ping),
            ]),
            ft.Container(health_text, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
        ])

    def view_seed(self, page: ft.Page):
        days = ft.TextField(label="Days of demo data", value="7", width=200)
        locs = ft.TextField(label="Locations (comma-separated)", value="Downtown,Uptown", width=400)

        def do_seed(_):
            try:
                payload = {
                    "days": int(days.value or 7),
                    "locations": [s.strip() for s in (locs.value or "").split(",") if s.strip()],
                }
                r = requests.post(self.backend + "/seed", json=payload, timeout=30)
                r.raise_for_status()
                notify(page, "Seed complete")
            except Exception as ex:
                notify(page, f"Seed failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Seed Demo Data", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([days, locs]),
            ft.ElevatedButton("Seed", on_click=do_seed),
        ], spacing=10)

    def view_reservations(self, page: ft.Page):
        when = ft.TextField(label="When (ISO 8601)", value=datetime.now().replace(microsecond=0).isoformat(), width=300)
        party = ft.TextField(label="Party size", value="2", width=120)
        duration = ft.TextField(label="Duration min", value="90", width=150)
        name = ft.TextField(label="Customer name", width=250)
        phone = ft.TextField(label="Phone", width=200)
        notes = ft.TextField(label="Notes", width=300)
        result = ft.Text("—")

        def check_avail(_):
            try:
                params = {
                    "when": when.value,
                    "party_size": int(party.value or 2),
                    "duration_min": int(duration.value or 90),
                }
                r = requests.get(self.backend + "/availability", params=params, timeout=10)
                result.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Availability error: {ex}", ok=False)

        def make_res(_):
            try:
                payload = {
                    "when": when.value,
                    "party_size": int(party.value or 2),
                    "customer_name": name.value or "Walk-in",
                    "phone": phone.value or None,
                    "notes": notes.value or None,
                }
                r = requests.post(self.backend + f"/reservations?duration_min={int(duration.value or 90)}", json=payload, timeout=10)
                r.raise_for_status()
                result.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Reservation error: {ex}", ok=False)

        return ft.Column([
            ft.Text("Reservations", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([when, party, duration]),
            ft.Row([name, phone, notes]),
            ft.Row([
                ft.ElevatedButton("Check availability", on_click=check_avail),
                ft.ElevatedButton("Create reservation", on_click=make_res),
            ]),
            ft.Container(result, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8, width=800),
        ], spacing=10)

    def date_filters(self):
        today = date.today()
        start = ft.TextField(label="Start (YYYY-MM-DD)", value=str(today.replace(day=max(1, today.day-7))), width=180)
        end = ft.TextField(label="End (YYYY-MM-DD)", value=str(today), width=180)
        location = ft.TextField(label="Location (optional)", width=220)
        return start, end, location

    def view_analytics(self, page: ft.Page):
        s1, e1, loc = self.date_filters()
        daily = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Day")),
            ft.DataColumn(ft.Text("Location")),
            ft.DataColumn(ft.Text("Covers")),
        ], rows=[])

        def load_daily(_):
            try:
                params = {"start": s1.value, "end": e1.value}
                if loc.value:
                    params["location"] = loc.value
                r = requests.get(self.backend + "/analytics/covers/daily", params=params, timeout=15)
                r.raise_for_status()
                rows = r.json()
                daily.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(x["day"])), ft.DataCell(ft.Text(x["location"])), ft.DataCell(ft.Text(str(x["covers"])))]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Load daily failed: {ex}", ok=False)

        s2, e2, loc2 = self.date_filters()
        hourly = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Hour")),
            ft.DataColumn(ft.Text("Location")),
            ft.DataColumn(ft.Text("Covers")),
        ], rows=[])

        def load_hourly(_):
            try:
                params = {"start": s2.value, "end": e2.value}
                if loc2.value:
                    params["location"] = loc2.value
                r = requests.get(self.backend + "/analytics/covers/hourly", params=params, timeout=15)
                r.raise_for_status()
                rows = r.json()
                hourly.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(x["hour"])), ft.DataCell(ft.Text(x["location"])), ft.DataCell(ft.Text(str(x["covers"])))]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Load hourly failed: {ex}", ok=False)

        # Core metrics
        s3, e3, loc3 = self.date_filters()
        metrics_output = ft.Text("—")

        def load_metrics(_):
            try:
                params = {"start": s3.value, "end": e3.value}
                if loc3.value:
                    params["location"] = loc3.value
                r = requests.get(self.backend + "/analytics/core/metrics", params=params, timeout=15)
                r.raise_for_status()
                metrics_output.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Load metrics failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Analytics", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Daily covers"),
            ft.Row([s1, e1, loc, ft.ElevatedButton("Load", on_click=load_daily)]),
            ft.Container(content=daily, height=250),
            ft.Divider(),
            ft.Text("Hourly covers"),
            ft.Row([s2, e2, loc2, ft.ElevatedButton("Load", on_click=load_hourly)]),
            ft.Container(content=hourly, height=250),
            ft.Divider(),
            ft.Text("Core metrics"),
            ft.Row([s3, e3, loc3, ft.ElevatedButton("Load", on_click=load_metrics)]),
            ft.Container(metrics_output, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
        ], spacing=10)

    def view_recs(self, page: ft.Page):
        # Popular items
        s1, e1, loc1 = self.date_filters()
        topk = ft.TextField(label="Top K", value="10", width=120)
        popular_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Qty")),
        ], rows=[])

        def load_popular(_):
            try:
                params = {"top_k": int(topk.value or 10)}
                if s1.value: params["start"] = s1.value
                if e1.value: params["end"] = e1.value
                if loc1.value: params["location"] = loc1.value
                r = requests.get(self.backend + "/recs/popular", params=params, timeout=15)
                rows = r.json()
                popular_table.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(x["name"])), ft.DataCell(ft.Text(str(x["total_qty"])))]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Popular failed: {ex}", ok=False)

        # Co-occurrence
        items_dropdown = ft.Dropdown(label="Anchor item", width=300)

        def load_items():
            try:
                r = requests.get(self.backend + "/menu/items", timeout=10)
                r.raise_for_status()
                items = r.json()
                items_dropdown.options = [ft.dropdown.Option(f"{it['id']} - {it['name']}") for it in items]
                page.update()
            except Exception as ex:
                notify(page, f"Load items failed: {ex}", ok=False)

        co_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Co-orders")),
            ft.DataColumn(ft.Text("Attach rate")),
        ], rows=[])

        def load_co(_):
            try:
                if not items_dropdown.value:
                    notify(page, "Pick an anchor item", ok=False)
                    return
                anchor_id = int(items_dropdown.value.split(" - ")[0])
                params = {"anchor_item_id": anchor_id, "top_k": int(topk.value or 10)}
                if s1.value: params["start"] = s1.value
                if e1.value: params["end"] = e1.value
                if loc1.value: params["location"] = loc1.value
                r = requests.get(self.backend + "/recs/cooccurrence", params=params, timeout=15)
                rows = r.json()
                co_table.rows = [ft.DataRow(cells=[
                    ft.DataCell(ft.Text(x["name"])),
                    ft.DataCell(ft.Text(str(x["co_orders"]))),
                    ft.DataCell(ft.Text(str(x["attach_rate"]))),
                ]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Co-occurrence failed: {ex}", ok=False)

        load_items()

        return ft.Column([
            ft.Text("Recommendations", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([topk]),
            ft.Text("Popular items"),
            ft.Row([s1, e1, loc1, ft.ElevatedButton("Load popular", on_click=load_popular)]),
            ft.Container(popular_table, height=250),
            ft.Divider(),
            ft.Text("Co-occurrence"),
            items_dropdown,
            ft.Row([ft.ElevatedButton("Load co-occurrence", on_click=load_co)]),
            ft.Container(co_table, height=250),
        ], spacing=10)

    def view_reviews(self, page: ft.Page):
        loc = ft.TextField(label="Location", value="Downtown", width=200)
        ts = ft.TextField(label="Timestamp (ISO)", value=datetime.now().replace(microsecond=0).isoformat(), width=260)
        rating = ft.TextField(label="Rating (1-5)", value="5", width=120)
        text = ft.TextField(label="Text", multiline=True, min_lines=3, width=500)
        source = ft.TextField(label="Source", value="onsite", width=160)
        resp = ft.Text("—")

        def submit(_):
            try:
                payload = {"location": loc.value, "ts": ts.value, "rating": int(rating.value or 5), "text": text.value, "source": source.value}
                r = requests.post(self.backend + "/reviews", json=payload, timeout=15)
                r.raise_for_status()
                resp.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Add review failed: {ex}", ok=False)

        s1, e1, loc1 = self.date_filters()
        summary = ft.Text("—")

        def load_summary(_):
            try:
                params = {"start": s1.value, "end": e1.value}
                if loc1.value: params["location"] = loc1.value
                r = requests.get(self.backend + "/reviews/summary", params=params, timeout=15)
                r.raise_for_status()
                summary.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Summary failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Reviews & NLP", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Add review"),
            ft.Row([loc, ts, rating, source]),
            text,
            ft.ElevatedButton("Submit", on_click=submit),
            ft.Divider(),
            ft.Text("Summary"),
            ft.Row([s1, e1, loc1, ft.ElevatedButton("Load summary", on_click=load_summary)]),
            ft.Container(summary, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
        ])

    def view_inventory(self, page: ft.Page):
        loc = ft.TextField(label="Location (optional)", width=220)
        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Ingredient")),
            ft.DataColumn(ft.Text("Unit")),
            ft.DataColumn(ft.Text("Location")),
            ft.DataColumn(ft.Text("On hand")),
        ], rows=[])

        def load(_):
            try:
                params = {}
                if loc.value: params["location"] = loc.value
                r = requests.get(self.backend + "/inventory/onhand", params=params, timeout=15)
                r.raise_for_status()
                rows = r.json()
                table.rows = [ft.DataRow(cells=[
                    ft.DataCell(ft.Text(x["ingredient"])),
                    ft.DataCell(ft.Text(x["unit"])),
                    ft.DataCell(ft.Text(x["location"])),
                    ft.DataCell(ft.Text(str(x["on_hand"]))),
                ]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Load on-hand failed: {ex}", ok=False)

        ing = ft.TextField(label="Ingredient", width=220)
        loc2 = ft.TextField(label="Location", width=220)
        delta = ft.TextField(label="Delta (+/-)", width=150)

        def adjust(_):
            try:
                payload = {"ingredient": ing.value, "location": loc2.value, "delta": float(delta.value)}
                r = requests.post(self.backend + "/inventory/adjust", json=payload, timeout=15)
                r.raise_for_status()
                notify(page, f"Adjusted {ing.value} at {loc2.value}")
                load(None)
            except Exception as ex:
                notify(page, f"Adjust failed: {ex}", ok=False)

        s1, e1, loc3 = self.date_filters()
        usage_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Ingredient")),
            ft.DataColumn(ft.Text("Unit")),
            ft.DataColumn(ft.Text("Used")),
        ], rows=[])

        def usage(_):
            try:
                params = {"start": s1.value, "end": e1.value}
                if loc3.value: params["location"] = loc3.value
                r = requests.get(self.backend + "/inventory/usage", params=params, timeout=15)
                rows = r.json()
                usage_table.rows = [ft.DataRow(cells=[
                    ft.DataCell(ft.Text(x["ingredient"])),
                    ft.DataCell(ft.Text(x["unit"])),
                    ft.DataCell(ft.Text(str(x["used"]))),
                ]) for x in rows]
                page.update()
            except Exception as ex:
                notify(page, f"Usage failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Inventory", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([loc, ft.ElevatedButton("Load on-hand", on_click=load)]),
            ft.Container(table, height=250),
            ft.Divider(),
            ft.Text("Adjust"),
            ft.Row([ing, loc2, delta, ft.ElevatedButton("Apply", on_click=adjust)]),
            ft.Divider(),
            ft.Text("Usage"),
            ft.Row([s1, e1, loc3, ft.ElevatedButton("Load usage", on_click=usage)]),
            ft.Container(usage_table, height=250),
        ], spacing=10)

    def view_customers(self, page: ft.Page):
        name = ft.TextField(label="Name", width=220)
        email = ft.TextField(label="Email", width=220)
        phone = ft.TextField(label="Phone", width=180)
        marketing = ft.Switch(label="Marketing consent", value=False)
        analytics = ft.Switch(label="Analytics consent", value=True)
        resp = ft.Text("—")

        def create(_):
            try:
                payload = {
                    "name": name.value or None,
                    "email": email.value or None,
                    "phone": phone.value or None,
                    "marketing_consent": bool(marketing.value),
                    "analytics_consent": bool(analytics.value),
                }
                r = requests.post(self.backend + "/customers", json=payload, timeout=15)
                r.raise_for_status()
                resp.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Create customer failed: {ex}", ok=False)

        cust_id = ft.TextField(label="Customer ID", width=150)
        get_out = ft.Text("—")

        def get_one(_):
            try:
                cid = int(cust_id.value)
                r = requests.get(self.backend + f"/customers/{cid}", timeout=10)
                r.raise_for_status()
                get_out.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Get customer failed: {ex}", ok=False)

        m2 = ft.Switch(label="Marketing", value=False)
        a2 = ft.Switch(label="Analytics", value=True)
        upd_out = ft.Text("—")

        def upd(_):
            try:
                cid = int(cust_id.value)
                payload = {"marketing_consent": bool(m2.value), "analytics_consent": bool(a2.value)}
                r = requests.patch(self.backend + f"/customers/{cid}/consent", json=payload, timeout=10)
                r.raise_for_status()
                upd_out.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Update consent failed: {ex}", ok=False)

        pii = ft.Text("—")

        def load_pii(_):
            try:
                r = requests.get(self.backend + "/governance/pii_inventory", timeout=10)
                pii.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"PII inventory failed: {ex}", ok=False)

        entity = ft.TextField(label="Entity (orders|reviews|customers)", width=250)
        days = ft.TextField(label="Days", value="30", width=120)

        def upsert_policy(_):
            try:
                payload = {"entity": entity.value, "days": int(days.value)}
                r = requests.post(self.backend + "/governance/retention/policies", json=payload, timeout=10)
                r.raise_for_status()
                notify(page, "Policy saved")
            except Exception as ex:
                notify(page, f"Save policy failed: {ex}", ok=False)

        list_policies = ft.Text("—")

        def load_policies(_):
            try:
                r = requests.get(self.backend + "/governance/retention/policies", timeout=10)
                list_policies.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"List policies failed: {ex}", ok=False)

        apply_out = ft.Text("—")

        def apply_retention(_):
            try:
                r = requests.post(self.backend + "/governance/retention/apply", timeout=10)
                apply_out.value = str(r.json())
                page.update()
            except Exception as ex:
                notify(page, f"Apply retention failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Customers & Governance", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Create customer"),
            ft.Row([name, email, phone, marketing, analytics]),
            ft.ElevatedButton("Create", on_click=create),
            ft.Container(resp, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
            ft.Divider(),
            ft.Text("Get / Update"),
            ft.Row([cust_id, ft.ElevatedButton("Get", on_click=get_one), ft.ElevatedButton("Update consent", on_click=upd)]),
            ft.Container(get_out, padding=10),
            ft.Container(upd_out, padding=10),
            ft.Divider(),
            ft.Text("PII Inventory"),
            ft.ElevatedButton("Load PII", on_click=load_pii),
            ft.Container(pii, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
            ft.Divider(),
            ft.Text("Retention"),
            ft.Row([entity, days, ft.ElevatedButton("Save policy", on_click=upsert_policy), ft.ElevatedButton("List", on_click=load_policies), ft.ElevatedButton("Apply", on_click=apply_retention)]),
            ft.Container(list_policies, padding=10),
            ft.Container(apply_out, padding=10),
        ], spacing=10)

    def view_exports(self, page: ft.Page):
        s1, e1, loc = self.date_filters()
        links = ft.Text("—")

        def gen_links(_):
            try:
                params = f"start={s1.value}&end={e1.value}"
                if loc.value:
                    params += f"&location={loc.value}"
                base = self.backend
                links.value = "\n".join([
                    base + "/exports/daily_covers.csv?" + params,
                    base + "/exports/item_sales.csv?" + params,
                ])
                page.update()
            except Exception as ex:
                notify(page, f"Build export links failed: {ex}", ok=False)

        return ft.Column([
            ft.Text("Exports", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([s1, e1, loc, ft.ElevatedButton("Build links", on_click=gen_links)]),
            ft.Text("Open these URLs in your browser to download:"),
            ft.Container(links, padding=10, bgcolor=ft.Colors.BLUE_GREY_900, border_radius=8),
        ])

    # --------------- App ---------------
    def main(self, page: ft.Page):
        page.title = "RestaurantIA Console"
        page.theme_mode = "dark"
        page.padding = 16
        page.scroll = ft.ScrollMode.AUTO

        tabs = ft.Tabs(expand=1, tabs=[
            ft.Tab(text="Health", icon=ft.Icons.HEALTH_AND_SAFETY, content=self.view_health(page)),
            ft.Tab(text="Seed", icon=ft.Icons.SEEDLING, content=self.view_seed(page)),
            ft.Tab(text="Reservations", icon=ft.Icons.EVENT, content=self.view_reservations(page)),
            ft.Tab(text="Analytics", icon=ft.Icons.INSIGHTS, content=self.view_analytics(page)),
            ft.Tab(text="Recommendations", icon=ft.Icons.RECOMMEND, content=self.view_recs(page)),
            ft.Tab(text="Reviews", icon=ft.Icons.REVIEWS, content=self.view_reviews(page)),
            ft.Tab(text="Inventory", icon=ft.Icons.INVENTORY, content=self.view_inventory(page)),
            ft.Tab(text="Customers", icon=ft.Icons.PEOPLE, content=self.view_customers(page)),
            ft.Tab(text="Exports", icon=ft.Icons.DOWNLOAD, content=self.view_exports(page)),
        ])

        page.add(tabs)


def main():
    app = RestaurantFrontend()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
