[![Flash Flood API Pipeline](https://github.com/Beptoo/flash-flood-api/actions/workflows/pipeline.yml/badge.svg)](https://github.com/Beptoo/flash-flood-api/actions/workflows/pipeline.yml)
# Flash Flood Early Warning System API

Project tugas individu untuk membuat RESTful API sederhana pakai Flask, dilengkapi Docker dan GitHub Actions.

## Tujuan Tugas
- CRUD data sensor ketinggian air
- Response JSON konsisten
- Bisa jalan di lokal dan Docker
- Ada automation testing (CI) dan security scan (CS)

## Fitur Utama
- CRUD endpoint: GET, POST, PUT, PATCH, DELETE
- Format response:

```json
{
  "status": "OK",
  "data": {},
  "message": "...",
  "errors": null
}
```

- Validasi input dasar:
  - location: string
  - water_level: number
  - unit: cm atau m
  - recorded_at: string
  - status_level: normal/warning/danger

## Struktur File
- app.py
- test_app.py
- requirements.txt
- Dockerfile
- docker-compose.yml
- .github/workflows/pipeline.yml

## Cara Menjalankan

### 1) Lokal (Python)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API jalan di:
- http://127.0.0.1:5000

### 2) Docker

```bash
docker compose up --build
```

Kalau pakai Docker versi lama:

```bash
docker-compose up --build
```

## Testing

```bash
pytest -v
```

File test:
- test_app.py

## Ringkasan Endpoint
- GET /
- GET /sensors
- GET /sensors/<id>
- POST /sensors
- PUT /sensors/<id>
- PATCH /sensors/<id>
- DELETE /sensors/<id>

## Contoh Request Cepat

### Create Sensor

```bash
curl -X POST http://127.0.0.1:5000/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "location": "River Gate A",
    "water_level": 123.4,
    "unit": "cm",
    "recorded_at": "2026-03-24T10:30:00Z",
    "status_level": "warning"
  }'
```

### Get All Sensors

```bash
curl http://127.0.0.1:5000/sensors
```

## GitHub Actions
Workflow otomatis jalan saat:
- push ke main/develop
- pull request ke main/develop

Job:
- CI: run pytest
- CS: run gitleaks scan

