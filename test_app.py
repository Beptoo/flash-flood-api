import pytest
import json

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def sample_sensor():
    """Sample sensor data untuk testing"""
    return {
        "location": "River Gate A",
        "water_level": 123.4,
        "unit": "cm",
        "recorded_at": "2026-03-24T10:30:00Z",
        "status_level": "warning",
    }


@pytest.fixture
def sample_sensor_2():
    """Sample sensor data kedua untuk testing"""
    return {
        "location": "River Gate B",
        "water_level": 50.5,
        "unit": "m",
        "recorded_at": "2026-03-24T11:00:00Z",
        "status_level": "normal",
    }


# ==================== GET ALL SENSORS TESTS ====================

class TestGetAllSensors:
    """Test cases untuk GET /sensors"""

    def test_get_sensors_returns_ok(self, client):
        """Test GET semua sensor - response format correct"""
        response = client.get("/sensors")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["status"] == "OK"
        assert isinstance(payload["data"], list)
        assert payload["errors"] is None
        assert "message" in payload

    def test_get_sensors_empty_database(self, client):
        """Test GET semua sensor ketika database kosong"""
        response = client.get("/sensors")
        payload = response.get_json()

        assert len(payload["data"]) == 0
        assert payload["message"] == "Sensors retrieved successfully"

    def test_get_sensors_with_data(self, client, sample_sensor):
        """Test GET semua sensor ketika ada data"""
        # Setup: tambah satu sensor
        client.post("/sensors", json=sample_sensor)

        # Test
        response = client.get("/sensors")
        payload = response.get_json()

        assert response.status_code == 200
        assert len(payload["data"]) == 1
        assert payload["data"][0]["location"] == "River Gate A"

    def test_get_sensors_multiple(self, client, sample_sensor, sample_sensor_2):
        """Test GET semua sensor dengan multiple data"""
        # Setup: tambah dua sensor
        client.post("/sensors", json=sample_sensor)
        client.post("/sensors", json=sample_sensor_2)

        # Test
        response = client.get("/sensors")
        payload = response.get_json()

        assert response.status_code == 200
        assert len(payload["data"]) == 2


# ==================== GET SENSOR BY ID TESTS ====================

class TestGetSensorById:
    """Test cases untuk GET /sensors/<id>"""

    def test_get_sensor_by_id_success(self, client, sample_sensor):
        """Test GET sensor berdasarkan ID yang valid"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Test
        response = client.get(f"/sensors/{sensor_id}")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["status"] == "OK"
        assert payload["data"]["id"] == sensor_id
        assert payload["data"]["location"] == "River Gate A"
        assert payload["errors"] is None

    def test_get_sensor_by_id_not_found(self, client):
        """Test GET sensor dengan ID yang tidak ada"""
        response = client.get("/sensors/9999")

        assert response.status_code == 404
        payload = response.get_json()
        assert payload["status"] == "ERROR"
        assert "Sensor not found" in payload["message"]
        assert payload["data"] is None

    def test_get_sensor_by_id_invalid_format(self, client):
        """Test GET sensor dengan ID format yang salah"""
        response = client.get("/sensors/invalid-id")

        assert response.status_code == 404  # 404 karena routing tidak cocok


# ==================== CREATE SENSOR TESTS ====================

class TestCreateSensor:
    """Test cases untuk POST /sensors"""

    def test_post_sensor_creates_data(self, client, sample_sensor):
        """Test create sensor dengan data yang valid"""
        response = client.post("/sensors", json=sample_sensor)

        assert response.status_code == 201
        payload = response.get_json()
        assert payload["status"] == "OK"
        assert payload["message"] == "Sensor created successfully"
        assert payload["data"]["id"] == 1
        assert payload["data"]["location"] == "River Gate A"
        assert payload["data"]["water_level"] == 123.4
        assert payload["data"]["unit"] == "cm"
        assert payload["errors"] is None

    def test_post_sensor_incremental_ids(self, client, sample_sensor, sample_sensor_2):
        """Test create multiple sensors dengan incremental IDs"""
        response1 = client.post("/sensors", json=sample_sensor)
        response2 = client.post("/sensors", json=sample_sensor_2)

        payload1 = response1.get_json()
        payload2 = response2.get_json()

        assert payload1["data"]["id"] == 1
        assert payload2["data"]["id"] == 2

    def test_post_sensor_missing_location(self, client):
        """Test create sensor tanpa field 'location'"""
        payload = {
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "ERROR"
        assert "location" in str(data["errors"]).lower()

    def test_post_sensor_missing_water_level(self, client):
        """Test create sensor tanpa field 'water_level'"""
        payload = {
            "location": "River A",
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "ERROR"
        assert "water_level" in str(data["errors"]).lower()

    def test_post_sensor_missing_unit(self, client):
        """Test create sensor tanpa field 'unit'"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "unit" in str(data["errors"]).lower()

    def test_post_sensor_missing_recorded_at(self, client):
        """Test create sensor tanpa field 'recorded_at'"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "recorded_at" in str(data["errors"]).lower()

    def test_post_sensor_invalid_water_level_type(self, client):
        """Test create sensor dengan water_level type salah"""
        payload = {
            "location": "River A",
            "water_level": "invalid",  # Harus numeric
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "water_level" in str(data["errors"]).lower()

    def test_post_sensor_invalid_unit(self, client):
        """Test create sensor dengan unit yang tidak valid"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "km",  # Harus "cm" atau "m"
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "unit" in str(data["errors"]).lower()

    def test_post_sensor_invalid_recorded_at_type(self, client):
        """Test create sensor dengan recorded_at type salah"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": 12345,  # Harus string (ISO datetime)
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "recorded_at" in str(data["errors"]).lower()

    def test_post_sensor_default_status_level(self, client):
        """Test create sensor tanpa status_level (should default to 'normal')"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["status_level"] == "normal"

    def test_post_sensor_explicit_status_level(self, client):
        """Test create sensor dengan status_level yang didefinisikan"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
            "status_level": "danger",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["status_level"] == "danger"

    def test_post_sensor_invalid_status_level(self, client):
        """Test create sensor dengan status_level yang tidak valid"""
        payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
            "status_level": "critical",  # Harus "normal", "warning", atau "danger"
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert "status_level" in str(data["errors"]).lower()

    def test_post_sensor_empty_json(self, client):
        """Test create sensor dengan empty JSON"""
        response = client.post("/sensors", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "ERROR"

    def test_post_sensor_null_json(self, client):
        """Test create sensor dengan null/no JSON"""
        response = client.post("/sensors")

        assert response.status_code == 400


# ==================== UPDATE SENSOR TESTS (PUT) ====================

class TestUpdateSensorPut:
    """Test cases untuk PUT /sensors/<id>"""

    def test_put_sensor_full_update(self, client, sample_sensor):
        """Test PUT untuk full update sensor"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Update dengan PUT
        update_payload = {
            "location": "River Gate C",
            "water_level": 200.0,
            "unit": "m",
            "recorded_at": "2026-03-24T12:00:00Z",
            "status_level": "danger",
        }
        response = client.put(f"/sensors/{sensor_id}", json=update_payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "OK"
        assert data["message"] == "Sensor updated successfully"
        assert data["data"]["location"] == "River Gate C"
        assert data["data"]["water_level"] == 200.0
        assert data["data"]["unit"] == "m"
        assert data["data"]["status_level"] == "danger"

    def test_put_sensor_not_found(self, client):
        """Test PUT sensor dengan ID yang tidak ada"""
        update_payload = {
            "location": "River A",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.put("/sensors/9999", json=update_payload)

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "ERROR"

    def test_put_sensor_missing_required_field(self, client, sample_sensor):
        """Test PUT dengan missing required field"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Update tanpa water_level
        update_payload = {
            "location": "River A",
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.put(f"/sensors/{sensor_id}", json=update_payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "ERROR"


# ==================== UPDATE SENSOR TESTS (PATCH) ====================

class TestUpdateSensorPatch:
    """Test cases untuk PATCH /sensors/<id>"""

    def test_patch_sensor_partial_update(self, client, sample_sensor):
        """Test PATCH untuk partial update sensor"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Update hanya water_level dengan PATCH
        update_payload = {"water_level": 250.0}
        response = client.patch(f"/sensors/{sensor_id}", json=update_payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "OK"
        assert data["message"] == "Sensor updated successfully"
        assert data["data"]["water_level"] == 250.0
        # Verify field lain tidak berubah
        assert data["data"]["location"] == "River Gate A"
        assert data["data"]["unit"] == "cm"

    def test_patch_sensor_update_status_only(self, client, sample_sensor):
        """Test PATCH update hanya status_level"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Update hanya status_level
        update_payload = {"status_level": "normal"}
        response = client.patch(f"/sensors/{sensor_id}", json=update_payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["status_level"] == "normal"
        # Verify field lain tetap sama
        assert data["data"]["water_level"] == 123.4

    def test_patch_sensor_not_found(self, client):
        """Test PATCH sensor dengan ID yang tidak ada"""
        response = client.patch("/sensors/9999", json={"water_level": 100.0})

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "ERROR"

    def test_patch_sensor_invalid_type(self, client, sample_sensor):
        """Test PATCH dengan tipe data yang salah"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # PATCH dengan water_level string
        update_payload = {"water_level": "invalid"}
        response = client.patch(f"/sensors/{sensor_id}", json=update_payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "ERROR"


# ==================== DELETE SENSOR TESTS ====================

class TestDeleteSensor:
    """Test cases untuk DELETE /sensors/<id>"""

    def test_delete_sensor_success(self, client, sample_sensor):
        """Test delete sensor yang ada"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Delete
        response = client.delete(f"/sensors/{sensor_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "OK"
        assert data["message"] == "Sensor deleted successfully"
        assert data["data"]["id"] == sensor_id

    def test_delete_sensor_verify_deleted(self, client, sample_sensor):
        """Test verify sensor sudah benar-benar dihapus"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Delete
        client.delete(f"/sensors/{sensor_id}")

        # Verify deleted
        get_response = client.get(f"/sensors/{sensor_id}")
        assert get_response.status_code == 404

    def test_delete_sensor_not_found(self, client):
        """Test delete sensor dengan ID yang tidak ada"""
        response = client.delete("/sensors/9999")

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "ERROR"
        assert "Sensor not found" in data["message"]

    def test_delete_sensor_twice(self, client, sample_sensor):
        """Test delete sensor dua kali (second delete should fail)"""
        # Setup: create sensor
        create_response = client.post("/sensors", json=sample_sensor)
        sensor_id = create_response.get_json()["data"]["id"]

        # Delete pertama
        response1 = client.delete(f"/sensors/{sensor_id}")
        assert response1.status_code == 200

        # Delete kedua - should fail
        response2 = client.delete(f"/sensors/{sensor_id}")
        assert response2.status_code == 404


# ==================== EDGE CASES TESTS ====================

class TestEdgeCases:
    """Test cases untuk edge cases dan error handling"""

    def test_post_with_float_water_level(self, client):
        """Test create sensor dengan float water_level"""
        payload = {
            "location": "River A",
            "water_level": 123.456789,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 201
        assert response.get_json()["data"]["water_level"] == 123.456789

    def test_post_with_integer_water_level(self, client):
        """Test create sensor dengan integer water_level"""
        payload = {
            "location": "River A",
            "water_level": 100,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 201
        assert response.get_json()["data"]["water_level"] == 100

    def test_location_with_special_characters(self, client):
        """Test create sensor dengan location yang punya special characters"""
        payload = {
            "location": "River Gate A & B #1 (North)",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        assert response.status_code == 201
        assert response.get_json()["data"]["location"] == "River Gate A & B #1 (North)"

    def test_empty_location_string(self, client):
        """Test create sensor dengan location empty string"""
        payload = {
            "location": "",
            "water_level": 100.0,
            "unit": "cm",
            "recorded_at": "2026-03-24T10:30:00Z",
        }
        response = client.post("/sensors", json=payload)

        # Empty string is technically valid, but might want to validate against this
        # For now, API accepts it
        assert response.status_code == 201


# ==================== INDEX ROUTE TESTS ====================

class TestIndexRoute:
    """Test cases untuk root endpoint"""

    def test_index_returns_ok(self, client):
        """Test index endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["status"] == "OK"
        assert "Flash Flood Early Warning System" in payload["message"]
