from datetime import datetime


class TestDonateEndpoint:
    async def test_post_donate_returns_201(self, client):
        resp = await client.post(
            "/donate",
            json={"name": "Alice", "value": 10.0, "date": datetime.now().isoformat()},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Alice"
        assert data["value"] == 10.0
        assert "id" in data

    async def test_get_balance_with_donations(self, client):
        # seed a donation
        await client.post(
            "/donate",
            json={"name": "Bob", "value": 25.0, "date": datetime.now().isoformat()},
        )
        await client.post(
            "/donate",
            json={"name": "Twizufr", "value": 25.0, "date": datetime.now().isoformat()},
        )
        resp = await client.get("/balance")
        assert resp.status_code == 200
        assert resp.json()["total"] == 50.0

    async def test_get_empty_balance_returns_zero(self, client):
        resp = await client.get("/balance")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0.0


class TestWidgetEndpoints:
    async def test_create_widget(self, client):
        resp = await client.post(
            "/widget/",
            json={
                "name": "test_widget",
                "timeout": 5,
                "showtime": 3,
                "template": "<div>test</div>",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test_widget"
        assert "id" in data

    async def test_get_widget_by_id(self, client):
        create_resp = await client.post(
            "/widget/",
            json={
                "name": "lookup",
                "timeout": 1,
                "showtime": 1,
                "template": "<span/>",
            },
        )
        widget_id = create_resp.json()["id"]

        resp = await client.get(f"/widget/{widget_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "lookup"

    async def test_get_nonexistent_widget_returns_404(self, client):
        resp = await client.get("/widget/999")
        assert resp.status_code == 404

    async def test_get_all_widgets_empty(self, client):
        resp = await client.get("/widget/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_all_widgets_with_data(self, client):
        await client.post(
            "/widget/",
            json={
                "name": "w1",
                "timeout": 1,
                "showtime": 1,
                "template": "<w1/>",
            },
        )
        resp = await client.get("/widget/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_create_widget_without_showtime_uses_settings_default(self, client):
        resp = await client.post(
            "/widget/",
            json={"name": "no_showtime", "timeout": 5, "template": "<div/>"},
        )
        assert resp.status_code == 201
        assert resp.json()["showtime"] == 30  # settings default


class TestErrorEnvelope:
    async def test_not_found_returns_envelope(self, client):
        resp = await client.get("/widget/999")

        assert resp.status_code == 404
        body = resp.json()
        assert body["error"] == "not_found"
        assert body["detail"] == "WidgetNotFoundError"

    async def test_not_found_envelope_on_page_route(self, client):
        resp = await client.get("/page/999")

        assert resp.status_code == 404
        body = resp.json()
        assert body["error"] == "not_found"
        assert body["detail"] == "WidgetNotFoundError"

    async def test_not_found_envelope_keys(self, client):
        not_found = (await client.get("/widget/999")).json()

        assert set(not_found.keys()) == {"error", "detail"}
