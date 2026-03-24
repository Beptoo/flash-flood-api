from flask import Flask, jsonify, request


def create_response(status: str = "OK", data=None, message: str = "", errors=None):
    return {
        "status": status,
        "data": data,
        "message": message,
        "errors": errors,
    }


def create_app():
    app = Flask(__name__)
    app.config["SENSORS"] = {}
    app.config["NEXT_ID"] = 1

    def validate_sensor_payload(payload, partial=False):
        required_fields = ["location", "water_level", "unit", "recorded_at"]
        errors = []

        if not isinstance(payload, dict):
            return ["Invalid JSON payload"]

        if not partial:
            for field in required_fields:
                if field not in payload:
                    errors.append(f"Field '{field}' is required")

        if "location" in payload and not isinstance(payload.get("location"), str):
            errors.append("Field 'location' must be a string")

        if "water_level" in payload and not isinstance(payload.get("water_level"), (int, float)):
            errors.append("Field 'water_level' must be a number")

        if "unit" in payload and payload.get("unit") not in {"cm", "m"}:
            errors.append("Field 'unit' must be either 'cm' or 'm'")

        if "recorded_at" in payload and not isinstance(payload.get("recorded_at"), str):
            errors.append("Field 'recorded_at' must be an ISO datetime string")

        if "status_level" in payload and payload.get("status_level") not in {"normal", "warning", "danger"}:
            errors.append("Field 'status_level' must be one of: normal, warning, danger")

        return errors

    @app.get("/")
    def index():
        return jsonify(create_response(message="Flash Flood Early Warning System API is running", data=None)), 200

    @app.get("/sensors")
    def get_sensors():
        sensors = list(app.config["SENSORS"].values())
        return jsonify(create_response(data=sensors, message="Sensors retrieved successfully", errors=None)), 200

    @app.get("/sensors/<int:sensor_id>")
    def get_sensor(sensor_id):
        sensor = app.config["SENSORS"].get(sensor_id)
        if sensor is None:
            return jsonify(create_response(status="ERROR", data=None, message="Sensor not found", errors=["Sensor ID does not exist"])), 404

        return jsonify(create_response(data=sensor, message="Sensor retrieved successfully", errors=None)), 200

    @app.post("/sensors")
    def create_sensor():
        payload = request.get_json(silent=True)
        errors = validate_sensor_payload(payload, partial=False)
        if errors:
            return jsonify(create_response(status="ERROR", data=None, message="Validation failed", errors=errors)), 400

        sensor_id = app.config["NEXT_ID"]
        app.config["NEXT_ID"] += 1

        sensor = {
            "id": sensor_id,
            "location": payload["location"],
            "water_level": payload["water_level"],
            "unit": payload["unit"],
            "recorded_at": payload["recorded_at"],
            "status_level": payload.get("status_level", "normal"),
        }

        app.config["SENSORS"][sensor_id] = sensor
        return jsonify(create_response(data=sensor, message="Sensor created successfully", errors=None)), 201

    @app.put("/sensors/<int:sensor_id>")
    @app.patch("/sensors/<int:sensor_id>")
    def update_sensor(sensor_id):
        sensor = app.config["SENSORS"].get(sensor_id)
        if sensor is None:
            return jsonify(create_response(status="ERROR", data=None, message="Sensor not found", errors=["Sensor ID does not exist"])), 404

        payload = request.get_json(silent=True)
        is_patch = request.method == "PATCH"
        errors = validate_sensor_payload(payload, partial=is_patch)
        if errors:
            return jsonify(create_response(status="ERROR", data=None, message="Validation failed", errors=errors)), 400

        if request.method == "PUT":
            sensor["location"] = payload["location"]
            sensor["water_level"] = payload["water_level"]
            sensor["unit"] = payload["unit"]
            sensor["recorded_at"] = payload["recorded_at"]
            sensor["status_level"] = payload.get("status_level", "normal")
        else:
            for key in ["location", "water_level", "unit", "recorded_at", "status_level"]:
                if key in payload:
                    sensor[key] = payload[key]

        app.config["SENSORS"][sensor_id] = sensor
        return jsonify(create_response(data=sensor, message="Sensor updated successfully", errors=None)), 200

    @app.delete("/sensors/<int:sensor_id>")
    def delete_sensor(sensor_id):
        sensor = app.config["SENSORS"].pop(sensor_id, None)
        if sensor is None:
            return jsonify(create_response(status="ERROR", data=None, message="Sensor not found", errors=["Sensor ID does not exist"])), 404

        return jsonify(create_response(data=sensor, message="Sensor deleted successfully", errors=None)), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
