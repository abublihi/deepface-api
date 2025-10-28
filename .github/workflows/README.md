# GitHub Actions CI/CD Pipeline

This directory contains the GitHub Actions workflows for automated testing, building, and deployment of the DeepFace API.

## Workflows

### `ci.yml` - Main CI/CD Pipeline

This workflow runs on every push and pull request to `main` and `develop` branches.

#### Jobs Overview

1. **Lint and Code Quality** 🧹
   - Runs `flake8` for syntax errors and code quality
   - Checks code formatting with `black`
   - Validates import sorting with `isort`

2. **Run Tests** 🧪
   - Sets up Python 3.10 environment
   - Installs system dependencies (libgl1, libglib2.0-0, libgomp1)
   - Caches DeepFace models to speed up subsequent runs
   - Runs pytest with all test cases
   - Generates coverage reports

3. **Build Docker Image** 🐳
   - Builds Docker image using BuildX
   - Caches Docker layers for faster builds
   - Tests the built image by running a container
   - Verifies the container starts successfully

4. **Security Scan** 🔒
   - Runs Trivy vulnerability scanner
   - Uploads results to GitHub Security tab
   - Identifies vulnerabilities in dependencies

5. **Publish Docker Image** 📦 (Main branch only)
   - Pushes Docker image to Docker Hub
   - Tags with `latest`, branch name, and git SHA
   - Only runs on successful merge to `main`

## Setup Instructions

### 1. Enable GitHub Actions

GitHub Actions is enabled by default for public repositories. For private repos, go to:
- Repository Settings → Actions → General → Allow all actions

### 2. Configure Secrets (For Docker Publishing)

To enable Docker image publishing to Docker Hub, add these secrets:

**Go to:** Repository Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `DOCKER_USERNAME` | Your Docker Hub username | Your Docker Hub login |
| `DOCKER_PASSWORD` | Docker Hub access token | [Create at Docker Hub](https://hub.docker.com/settings/security) |

**Creating Docker Hub Access Token:**
1. Login to [Docker Hub](https://hub.docker.com)
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Give it a name (e.g., "GitHub Actions")
5. Copy the token and add it as `DOCKER_PASSWORD` secret

### 3. Customize Workflow (Optional)

Edit `.github/workflows/ci.yml` to customize:

```yaml
env:
  PYTHON_VERSION: '3.10'           # Change Python version if needed
  DOCKER_IMAGE_NAME: deepface-api  # Change Docker image name
```

**Branch triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]    # Add/remove branches
  pull_request:
    branches: [ main, develop ]
```

## Workflow Triggers

The pipeline runs on:
- ✅ Push to `main` or `develop` branches
- ✅ Pull requests targeting `main` or `develop`
- ✅ Manual trigger via `workflow_dispatch`

## Caching Strategy

The workflow uses caching to speed up builds:

| Cache | Purpose | Speed Improvement |
|-------|---------|-------------------|
| Pip packages | Python dependencies | ~2-3 minutes |
| DeepFace models | Pre-trained AI models | ~5-10 minutes |
| Docker layers | Docker build cache | ~3-5 minutes |

## Understanding Job Dependencies

```
lint
  ↓
test (requires lint to pass)
  ↓
docker-build (requires test to pass)
  ↓
security-scan (requires docker-build)
  ↓
docker-publish (only on main branch)
```

## Viewing Results

### Test Results
1. Go to **Actions** tab in your repository
2. Click on the latest workflow run
3. Click on "Run Tests" job
4. Expand "Run pytest" step to see test results

### Coverage Report
Coverage reports are uploaded as artifacts:
1. Go to workflow run
2. Scroll to bottom → **Artifacts** section
3. Download `coverage-report`

### Security Scan
Security vulnerabilities are reported in:
1. **Security** tab → **Code scanning alerts**

### Docker Image
Published images are available at:
```
docker pull <your-dockerhub-username>/deepface-api:latest
```

## Local Testing

Test the workflow locally before pushing:

### Run tests locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term
```

### Test Docker build:
```bash
# Build image
docker build -t deepface-api:test .

# Run container
docker run -d -p 8000:8000 deepface-api:test

# Check logs
docker logs <container-id>
```

### Run linting:
```bash
# Install linting tools
pip install flake8 black isort

# Check syntax errors
flake8 app --select=E9,F63,F7,F82

# Check formatting
black --check app

# Check imports
isort --check-only app
```

## Troubleshooting

### Tests Failing in CI but Pass Locally

**Cause:** Missing system dependencies or model files

**Solution:**
- Check "Install system dependencies" step in workflow
- Ensure test images are not in `.dockerignore`
- Verify DeepFace models are cached correctly

### Docker Build Timeout

**Cause:** Model preloading takes too long

**Solution:**
- Increase timeout in workflow:
```yaml
- name: Build Docker image
  timeout-minutes: 30  # Add this line
```

### Docker Publish Fails

**Cause:** Missing or incorrect Docker Hub credentials

**Solution:**
1. Verify secrets are set: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
2. Ensure Docker Hub token has "Read, Write, Delete" permissions
3. Check Docker Hub repository exists

### Cache Not Working

**Cause:** Cache key changed or corrupted

**Solution:**
- Clear cache: Repository Settings → Actions → Caches → Delete cache
- Push again to regenerate cache

## Best Practices

✅ **Do:**
- Run tests locally before pushing
- Keep test images small (< 1MB each)
- Use meaningful commit messages
- Review security scan results

❌ **Don't:**
- Commit sensitive data (API keys, passwords)
- Push large files (> 100MB)
- Disable security scans
- Skip tests with `[skip ci]` unnecessarily

## Performance Optimization

### Faster Builds
- Caching reduces build time from ~15 minutes to ~5 minutes
- DeepFace model caching saves ~10 minutes per run
- Docker layer caching saves ~3-5 minutes

### Cost Optimization (GitHub Actions Minutes)
- Public repos: Unlimited free minutes ✅
- Private repos: 2,000 free minutes/month
- Average workflow run: ~10-15 minutes
- Caching reduces monthly minutes usage by ~60%

## Support

For issues with GitHub Actions:
1. Check workflow logs for detailed error messages
2. Review [GitHub Actions Documentation](https://docs.github.com/en/actions)
3. Open an issue in this repository

## Manual Workflow Dispatch

You can manually trigger the workflow:
1. Go to **Actions** tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Choose branch and click "Run workflow"