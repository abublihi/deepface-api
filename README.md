# DeepFace API

[![CI/CD Pipeline](https://github.com/abublihi/deepface-api/actions/workflows/ci.yml/badge.svg)](https://github.com/abublihi/deepface-api/actions/workflows/ci.yml)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A production-ready REST API for face recognition, verification, and analysis using DeepFace. Built with FastAPI and optimized for Docker deployment.

## Disclaimer

This application was developed with assistance from an AI tool. The author reviewed, tested, and edited the generated code and documentation, and is solely responsible for its correctness, security, and license compliance.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Endpoints](#-api-endpoints)
- [Usage Examples](#-usage-examples)
- [Docker Deployment](#-docker-deployment)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [License](#-license)

## 🏁 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/deepface_api.git
cd deepface_api

# Build the Docker image
docker build -t deepface-api .

# Run the container
docker run -d -p 8000:8000 deepface-api

# Access the API
curl http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📦 Installation

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)

### System Dependencies

For local development, install these system packages:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libgl1 libglib2.0-0 libgomp1
```

**macOS:**
```bash
brew install gcc
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

## 🔌 API Endpoints

### 1. Face Representation (`/represent`)

Extract face embeddings/features for face recognition.

**Endpoint:** `POST /represent`

**Parameters:**
- `img` (file): Image file containing a face
- `model_name` (string): Model to use (default: "SFace")
  - Options: SFace, VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, DeepID, ArcFace, Dlib
- `detector_backend` (string): Face detector (default: "yunet")
  - Options: opencv, ssd, dlib, mtcnn, retinaface, mediapipe, yolov8, yunet
- `enforce_detection` (bool): Enforce face detection (default: true)
- `align` (bool): Align face before processing (default: true)
- `anti_spoofing` (bool): Enable anti-spoofing detection (default: true)
- `max_faces` (int): Maximum number of faces to process (default: None)

**Response:**
```json
[
  {
    "embedding": [0.123, 0.456, ...],
    "facial_area": {
      "x": 100,
      "y": 150,
      "w": 200,
      "h": 250
    },
    "face_confidence": 0.98
  }
]
```

### 2. Face Analysis (`/analyze`)

Analyze facial attributes including age, gender, race, and emotions.

**Endpoint:** `POST /analyze`

**Parameters:**
- `img` (file): Image file containing a face
- `actions` (string): Comma-separated analysis actions (default: "age,gender,race,emotion")
  - Options: age, gender, race, emotion
- `detector_backend` (string): Face detector (default: "opencv")
- `enforce_detection` (bool): Enforce face detection (default: true)
- `align` (bool): Align face before processing (default: true)
- `anti_spoofing` (bool): Enable anti-spoofing detection (default: true)

**Response:**
```json
[
  {
    "age": 28,
    "dominant_gender": "Man",
    "gender": {
      "Man": 99.8,
      "Woman": 0.2
    },
    "dominant_race": "asian",
    "race": {
      "asian": 85.2,
      "white": 10.3,
      "black": 2.1,
      "indian": 1.5,
      "middle eastern": 0.6,
      "latino hispanic": 0.3
    },
    "dominant_emotion": "happy",
    "emotion": {
      "happy": 95.5,
      "neutral": 3.2,
      "surprise": 1.1,
      "sad": 0.1,
      "angry": 0.1,
      "fear": 0.0,
      "disgust": 0.0
    },
    "region": {
      "x": 100,
      "y": 150,
      "w": 200,
      "h": 250
    }
  }
]
```

### 3. Face Verification (`/verify`)

Verify if two faces belong to the same person.

**Endpoint:** `POST /verify`

**Parameters:**
- `img1` (file): First image file
- `img2` (file): Second image file
- `model_name` (string): Model to use (default: "SFace")
- `detector_backend` (string): Face detector (default: "yunet")
- `distance_metric` (string): Distance metric (default: "cosine")
  - Options: cosine, euclidean, euclidean_l2
- `enforce_detection` (bool): Enforce face detection (default: true)
- `align` (bool): Align face before processing (default: true)
- `anti_spoofing` (bool): Enable anti-spoofing detection (default: true)

**Response:**
```json
{
  "verified": true,
  "distance": 0.25,
  "threshold": 0.4,
  "model": "SFace",
  "detector_backend": "yunet",
  "similarity_metric": "cosine"
}
```

## 💡 Usage Examples

### cURL Examples

#### Represent (Extract Embeddings)
```bash
curl -X POST "http://localhost:8000/represent" \
  -F "img=@face.jpg" \
  -F "model_name=SFace" \
  -F "anti_spoofing=true"
```

#### Analyze Face
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "img=@face.jpg" \
  -F "actions=age,gender,race,emotion"
```

#### Verify Two Faces
```bash
curl -X POST "http://localhost:8000/verify" \
  -F "img1=@face1.jpg" \
  -F "img2=@face2.jpg" \
  -F "model_name=SFace"
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t deepface-api .

# Run with default settings (2 workers)
docker run -d -p 8000:8000 --name deepface deepface-api

# Run with custom worker count
docker run -d -p 8000:8000 \
  -e GUNICORN_WORKERS=4 \
  -e GUNICORN_TIMEOUT=180 \
  --name deepface deepface-api

# Check logs
docker logs deepface

# Stop and remove
docker stop deepface
docker rm deepface
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GUNICORN_WORKERS` | Number of Gunicorn worker processes | `2` |
| `GUNICORN_TIMEOUT` | Worker timeout in seconds | `120` |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |

### Gunicorn Configuration

Edit `gunicorn_conf.py` to customize:

```python
import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 5
graceful_timeout = 30
```

### Worker Count Recommendations

- **CPU-bound tasks**: Set workers = (2 × CPU cores) + 1
- **For 2 CPU cores**: 4-5 workers
- **For 4 CPU cores**: 8-9 workers
- **For 8 CPU cores**: 16-17 workers

## 🛠️ Development

### Project Structure

```
deepface_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── utils.py         # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API tests
│   ├── real_face.jpg    # Test images
│   └── spoofed_face.jpg
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions workflow
├── Dockerfile           # Docker configuration
├── .dockerignore        # Docker ignore rules
├── requirements.txt     # Python dependencies
├── gunicorn_conf.py     # Gunicorn configuration
└── README.md
```

### Running Locally

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive API docs
open http://localhost:8000/docs
```

### Code Quality

```bash
# Install linting tools
pip install flake8 black isort

# Check code style
flake8 app --max-line-length=127
black --check app
isort --check-only app

# Auto-format code
black app
isort app
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term --cov-report=html

# Run specific test
pytest tests/test_api.py::test_represent_real_image -v
```

## 🔄 CI/CD

### GitHub Actions Pipeline

The project includes automated CI/CD with GitHub Actions:

**Pipeline Stages:**
1. **Lint** - Code quality checks (flake8, black, isort)
2. **Test** - Run pytest suite with coverage
3. **Docker Build** - Build and test Docker image
4. **Security Scan** - Vulnerability scanning with Trivy
5. **Publish** - Push to Docker Hub (on main branch)

**Setup:**
1. Fork/clone the repository
2. Add secrets to GitHub:
   - `DOCKER_USERNAME` - Your Docker Hub username
   - `DOCKER_PASSWORD` - Docker Hub access token
3. Push to `main` or `develop` branch
4. View results in Actions tab

**Workflow Badge:**
```markdown
[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci.yml)
```

For detailed CI/CD documentation, see [.github/workflows/README.md](.github/workflows/README.md).

## 📝 License

This project is licensed under the MIT License.

## 🌷 Acknowledgments

- [DeepFace](https://github.com/serengil/deepface) - Face recognition library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Docker](https://www.docker.com/) - Containerization platform
