from datetime import datetime


class TestGetLastDonations:
    async def test_returns_empty_list_when_no_donations(self, client):
        resp = await client.get("/donations/last")
        assert resp.status_code == 200
        assert resp.json() == {"donations": []}

    async def test_returns_last_10_in_descending_order(self, client):
        for i in range(12):
            await client.post(
                "/donate",
                json={
                    "name": f"Donor{i}",
                    "value": float(i + 1),
                    "date": datetime(2024, 1, i + 1).isoformat(),
                },
            )

        resp = await client.get("/donations/last")
        assert resp.status_code == 200
        data = resp.json()["donations"]
        assert len(data) == 10
        # newest first
        assert data[0]["name"] == "Donor11"
        assert data[-1]["name"] == "Donor2"

    async def test_returns_htmx_fragment_with_hx_request_header(self, client):
        await client.post(
            "/donate",
            json={"name": "Alice", "value": 5.0, "date": datetime.now().isoformat()},
        )

        resp = await client.get(
            "/donations/last", headers={"HX-Request": "true"}
        )
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "Alice" in resp.text
        assert "5.0" in resp.text

    async def test_htmx_fragment_shows_empty_state(self, client):
        resp = await client.get(
            "/donations/last", headers={"HX-Request": "true"}
        )
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "No donations yet." in resp.text

    async def test_donations_page_renders_html(self, client):
        resp = await client.get("/page/donations")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "Last 10 donations" in resp.text
        assert 'hx-get="/donations/last"' in resp.text
