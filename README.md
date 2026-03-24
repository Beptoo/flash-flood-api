[![Flash Flood API Pipeline](https://github.com/Beptoo/flash-flood-api/actions/workflows/pipeline.yml/badge.svg)](https://github.com/Beptoo/flash-flood-api/actions/workflows/pipeline.yml)
# 🌊 Flash Flood Early Warning System API

RESTful API untuk sistem peringatan dini banjir bandang (Flash Flood) yang mengelola data sensor ketinggian air secara real-time dengan integrasi penuh Docker, GitHub Actions, dan monitoring otomatis.

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Tech Stack](#tech-stack)
- [Persyaratan](#persyaratan)
- [Setup & Installation](#setup--installation)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Request & Response Examples](#request--response-examples)
- [Error Handling](#error-handling)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

---

## ✨ Fitur

### Core Features
- ✅ **CRUD Operations**: Lengkap untuk manajemen data sensor (Create, Read, Update, Delete)
- ✅ **Standard JSON Response**: Konsisten dengan format `{status, data, message, errors}`
- ✅ **Input Validation**: Validasi komprehensif untuk semua field sensor
- ✅ **Error Handling**: HTTP status codes yang sesuai (200, 201, 400, 404, 500)
- ✅ **Health Check**: Endpoint monitoring untuk system availability
- ✅ **PUT/PATCH Support**: Full update dan partial update sensor

### DevOps Features
- 🐳 **Docker Support**: Containerization dengan Docker dan Docker Compose
- 🔒 **Security Scanning**: Gitleaks untuk deteksi credentials/secrets
- ✅ **Automated Testing**: CI pipeline dengan pytest di GitHub Actions
- 📊 **Code Coverage**: Coverage reporting dengan pytest-cov
- 🔄 **Hot Reload**: Volume mounting untuk development

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0.3 |
| **Testing** | pytest 8.3.2, pytest-cov 4.1.0 |
| **Environment** | python-dotenv 1.0.0 |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Security** | Gitleaks |

---

## 📦 Persyaratan

- **Docker**: >=20.10
- **Docker Compose**: >=1.29
- **Python**: >=3.10 (untuk local development)
- **Git**: >=2.28

### Optional (untuk development lokal tanpa Docker)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 🚀 Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/flood-warning-api.git
cd flood-warning-api
```

### 2. Konfigurasi Environment (Opsional)
Buat file `.env` untuk override default configuration:
```bash
cat > .env << EOF
FLASK_ENV=development
FLASK_APP=app.py
PYTHONUNBUFFERED=1
EOF
```

### 3. Setup Git hooks (Opsional, untuk pre-commit checks)
```bash
# Buat pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running tests before commit..."
pytest test_app.py -v
if [ $? -ne 0 ]; then
  echo "Tests failed! Commit aborted."
  exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## 🐳 Menjalankan Aplikasi

### Option 1: Menggunakan Docker Compose (Recommended)

```bash
# Build dan start container
docker-compose up --build

# Atau background mode
docker-compose up -d

# Cek status
docker-compose ps

# Stop container
docker-compose down
```

**Output yang diharapkan:**
```
flash-flood-api  | * Running on http://0.0.0.0:5000
```

API akan accessible di: `http://localhost:5000`

### Option 2: Local Development (Python)

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan Flask app
python app.py

# atau dengan Flask CLI
export FLASK_APP=app.py
flask run
```

### Health Check
```bash
# Cek apakah API running
curl http://localhost:5000/
# Expected response:
# {"status": "OK", "data": null, "message": "Flash Flood Early Warning System API is running", "errors": null}
```

---

## 🧪 Testing

### Run All Tests
```bash
# Menggunakan Docker Compose
docker-compose exec flash-flood-api pytest test_app.py -v

# Atau lokal
pytest test_app.py -v
```

### Run Tests dengan Coverage Report
```bash
# Generate coverage report
docker-compose exec flash-flood-api pytest test_app.py -v --cov=. --cov-report=html

# Atau lokal
pytest test_app.py -v --cov=. --cov-report=html

# Coverage report akan di: htmlcov/index.html
```

### Run Specific Test
```bash
# Test hanya class tertentu
pytest test_app.py::TestCreateSensor -v

# Test hanya function tertentu
pytest test_app.py::TestCreateSensor::test_post_sensor_creates_data -v
```

### Test Statistics
```
Total Test Cases: 40+
Coverage Target: >85%
```

---

## 📡 API Endpoints

### 1. Root Endpoint

**GET** `/`
```
Description: Health check endpoint
Status Code: 200 OK
```

### 2. Get All Sensors

**GET** `/sensors`
```
Description: Retrieve semua sensor data
Status Code: 200 OK
Query Parameters: None
```

### 3. Get Sensor By ID

**GET** `/sensors/<id>`
```
Description: Retrieve sensor berdasarkan ID
Status Code: 200 OK (found) | 404 Not Found
Path Parameters:
  - id: integer (required)
```

### 4. Create Sensor

**POST** `/sensors`
```
Description: Create sensor baru
Status Code: 201 Created | 400 Bad Request
Content-Type: application/json
Required Fields:
  - location: string
  - water_level: number (int/float)
  - unit: string ("cm" atau "m")
  - recorded_at: string (ISO 8601 datetime)
Optional Fields:
  - status_level: string ("normal", "warning", "danger") - default: "normal"
```

### 5. Update Sensor (Full)

**PUT** `/sensors/<id>`
```
Description: Full update sensor (semua field wajib ada)
Status Code: 200 OK | 400 Bad Request | 404 Not Found
Content-Type: application/json
Path Parameters:
  - id: integer (required)
Required Fields: Sama seperti POST /sensors
```

### 6. Update Sensor (Partial)

**PATCH** `/sensors/<id>`
```
Description: Partial update sensor (hanya field yang dikirim yg diupdate)
Status Code: 200 OK | 400 Bad Request | 404 Not Found
Content-Type: application/json
Path Parameters:
  - id: integer (required)
Optional Fields: Semua field sensor bersifat optional
```

### 7. Delete Sensor

**DELETE** `/sensors/<id>`
```
Description: Delete sensor
Status Code: 200 OK | 404 Not Found
Path Parameters:
  - id: integer (required)
```

---

## 📨 Request & Response Examples

### Example 1: Create Sensor (POST)

**Request:**
```bash
curl -X POST http://localhost:5000/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "location": "River Gate A",
    "water_level": 123.4,
    "unit": "cm",
    "recorded_at": "2026-03-24T10:30:00Z",
    "status_level": "warning"
  }'
```

**Response (201 Created):**
```json
{
  "status": "OK",
  "data": {
    "id": 1,
    "location": "River Gate A",
    "water_level": 123.4,
    "unit": "cm",
    "recorded_at": "2026-03-24T10:30:00Z",
    "status_level": "warning"
  },
  "message": "Sensor created successfully",
  "errors": null
}
```

### Example 2: Get All Sensors (GET)

**Request:**
```bash
curl http://localhost:5000/sensors
```

**Response (200 OK):**
```json
{
  "status": "OK",
  "data": [
    {
      "id": 1,
      "location": "River Gate A",
      "water_level": 123.4,
      "unit": "cm",
      "recorded_at": "2026-03-24T10:30:00Z",
      "status_level": "warning"
    },
    {
      "id": 2,
      "location": "River Gate B",
      "water_level": 50.5,
      "unit": "m",
      "recorded_at": "2026-03-24T11:00:00Z",
      "status_level": "normal"
    }
  ],
  "message": "Sensors retrieved successfully",
  "errors": null
}
```

### Example 3: Update Sensor (PATCH)

**Request:**
```bash
curl -X PATCH http://localhost:5000/sensors/1 \
  -H "Content-Type: application/json" \
  -d '{
    "water_level": 150.0,
    "status_level": "danger"
  }'
```

**Response (200 OK):**
```json
{
  "status": "OK",
  "data": {
    "id": 1,
    "location": "River Gate A",
    "water_level": 150.0,
    "unit": "cm",
    "recorded_at": "2026-03-24T10:30:00Z",
    "status_level": "danger"
  },
  "message": "Sensor updated successfully",
  "errors": null
}
```

### Example 4: Delete Sensor (DELETE)

**Request:**
```bash
curl -X DELETE http://localhost:5000/sensors/1
```

**Response (200 OK):**
```json
{
  "status": "OK",
  "data": {
    "id": 1,
    "location": "River Gate A",
    "water_level": 150.0,
    "unit": "cm",
    "recorded_at": "2026-03-24T10:30:00Z",
    "status_level": "danger"
  },
  "message": "Sensor deleted successfully",
  "errors": null
}
```

---

## ❌ Error Handling

### Error Response Format
```json
{
  "status": "ERROR",
  "data": null,
  "message": "Descriptive error message",
  "errors": ["Specific error 1", "Specific error 2"]
}
```

### Common Error Cases

#### 1. Validation Error (400 Bad Request)
```json
{
  "status": "ERROR",
  "data": null,
  "message": "Validation failed",
  "errors": [
    "Field 'location' is required",
    "Field 'water_level' must be a number"
  ]
}
```

#### 2. Resource Not Found (404 Not Found)
```json
{
  "status": "ERROR",
  "data": null,
  "message": "Sensor not found",
  "errors": ["Sensor ID does not exist"]
}
```

#### 3. Invalid Unit (400 Bad Request)
```json
{
  "status": "ERROR",
  "data": null,
  "message": "Validation failed",
  "errors": ["Field 'unit' must be either 'cm' or 'm'"]
}
```

#### 4. Invalid Status Level (400 Bad Request)
```json
{
  "status": "ERROR",
  "data": null,
  "message": "Validation failed",
  "errors": ["Field 'status_level' must be one of: normal, warning, danger"]
}
```

---

## 🚀 Deployment

### Deploy ke Production (Docker)

#### 1. Build Production Image
```bash
docker build -t flood-warning-api:1.0.0 .
```

#### 2. Run Container with Security Options
```bash
docker run \
  --name flood-api-prod \
  --restart always \
  --health-cmd='curl -f http://localhost:5000/ || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  flood-warning-api:1.0.0
```

#### 3. Or menggunakan Docker Compose Production Setup
```bash
# Create production override file
cat > docker-compose.prod.yml << EOF
version: "3.9"
services:
  flash-flood-api:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

# Run with override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Pipeline berjalan otomatis pada:
- ✅ `push` ke branch `main` atau `develop`
- ✅ `pull request` ke branch `main` atau `develop`

### Jobs dalam Pipeline

#### 1. **CI - Unit Testing**
- Setup Python 3.12
- Install dependencies
- Run pytest dengan verbose output
- Generate coverage report

#### 2. **CS - Security Scan**
- Checkout code
- Run Gitleaks untuk deteksi secrets
- Fail jika ada secrets terdeteksi

#### 3. **Build Docker Image** (hanya untuk push ke main)
- Setup Docker Buildx
- Build image tanpa push
- Cache untuk optimization

### Workflow File Location
`.github/workflows/pipeline.yml`

### View Pipeline Status
```bash
# Di GitHub UI: Actions tab
# Atau via GitHub CLI
gh run list
gh run view <run-id>
```

---

## 🐛 Troubleshooting

### Docker Issues

**Problem: Port 5000 already in use**
```bash
# Find process using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill process or use different port
docker-compose -e FLASK_PORT=5001 up
```

**Problem: Container exits immediately**
```bash
# Check logs
docker-compose logs flash-flood-api

# Rebuild image
docker-compose up --build
```

### Testing Issues

**Problem: Tests fail dengan "Module not found"**
```bash
# Install dependencies
pip install -r requirements.txt

# Atau dengan docker
docker-compose exec flash-flood-api pip install -r requirements.txt
```

**Problem: PYTHONUNBUFFERED not working**
```bash
# Set explicitly
export PYTHONUNBUFFERED=1
python app.py
```

### API Issues

**Problem: 404 Not Found saat akses endpoints**
```bash
# Verify server running
curl http://localhost:5000/

# Check Flask routing
python -c "from app import create_app; app = create_app(); print([rule for rule in app.url_map.iter_rules()])"
```

**Problem: JSON decode error**
```bash
# Ensure Content-Type header is set
curl -H "Content-Type: application/json" -d '{}' http://localhost:5000/sensors
```

---

## 📚 Useful Commands

### Docker Commands
```bash
# View logs
docker-compose logs -f flash-flood-api

# Execute command in container
docker-compose exec flash-flood-api bash

# Remove all containers and volumes
docker-compose down -v

# Rebuild without cache
docker-compose up --build --no-cache
```

### Git Commands
```bash
# View commit history
git log --oneline --graph

# Create feature branch
git checkout -b feature/new-feature

# Push to remote
git push -u origin feature/new-feature

# Create pull request
gh pr create --base main --fill
```

### Pytest Commands
```bash
# Run all tests
pytest -v

# Run specific test class
pytest test_app.py::TestCreateSensor -v

# Run with markers
pytest -v -m "not slow"

# Show print statements
pytest -v -s

# Stop on first failure
pytest -x
```

---

## 📝 Conventional Commits

Gunakan format ini untuk semua commit messages:

```
<type>(<scope>): <description>

<body>

<footer>
```

### Commit Types
- `feat:` - Fitur baru
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test cases
- `chore:` - Maintenance tasks
- `ci:` - CI/CD configuration

### Examples
```bash
git commit -m "feat(sensors): add water level threshold validation

- Add minimum water level check
- Add maximum water level check
- Return validation error for out-of-range values"

git commit -m "fix(api): handle null JSON in POST request"

git commit -m "test(endpoints): add 40+ comprehensive test cases"

git commit -m "ci: setup GitHub Actions CI/CD pipeline"
```

---

## 📞 Support & Contribution

Untuk laporan bug atau feature request, buat issue di GitHub repository.

---

## 📄 License

Proyek ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

---

**Last Updated:** March 24, 2026
**Version:** 1.0.0
**Maintained by:** Your Team
