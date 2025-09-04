# 🩺 Health Check Dashboard

[![CI/CD](https://github.com/The4ing/health-check-dashboard/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/The4ing/health-check-dashboard/actions)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Docker](https://img.shields.io/badge/Container-Docker-informational)
![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326ce5)
![License](https://img.shields.io/badge/License-MIT-green)

A lightweight dashboard for monitoring websites: checks response times and status (UP/DOWN), displays a table and live chart, allows adding/removing sites from the UI, and exposes Prometheus metrics for monitoring.

> 🐣 **Easter-egg**: _look for the hidden text_

---

## ✨ Features
- Website health checks (HTTP GET) with **UP/DOWN** status and **response time**
- Stylish table + live chart (Chart.js), auto-refresh every 10s
- Add/remove sites directly from the UI
- Persistent site list (`sites.txt`) survives restarts
- Endpoints:
  - `/` → UI
  - `/api` → JSON
  - `/metrics` → Prometheus metrics (Counters + Histogram)
- Ready-to-use Dockerfile + Kubernetes manifests (Deployment + Service)
- GitHub Actions CI/CD: lint/tests → build → Trivy scan → push to DockerHub (if configured)

---

## 🧭 Project Structure

```
.
├─ app/
│  ├─ main.py
│  └─ templates/
│     └─ index.html
├─ k8s/
│  ├─ deployment.yaml
│  └─ service.yaml
├─ tests/
│  └─ test_utils.py
├─ .github/workflows/ci-cd.yaml
├─ requirements.txt
├─ Dockerfile
└─ README.md
```

---

## 🚀 Quickstart

### Local (Python)
```bash
pip install -r requirements.txt
mkdir data
# Windows PowerShell:
$env:DATA_DIR="$PWD\data"
python app/main.py
# Browser: http://localhost:5000
```

### Docker
```bash
docker build -t health-check-dashboard .
docker run --name hcd -p 5000:5000 -e DATA_DIR=/data -v ${PWD}\data:/data health-check-dashboard
# http://localhost:5000
```

### Kubernetes (Minikube)
```bash
minikube start
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
minikube service health-check-svc
# or: http://<minikube-ip>:30080
```

---

## ⚙️ Configuration

| Variable   | Default   | Description |
|------------|-----------|-------------|
| `DATA_DIR` | `/data`   | Where to store `sites.txt` (persistent site list) |
| `SITES`    | defaults in code | Comma-separated site list; overrides file if set |

Example:
```bash
docker run -p 5000:5000 -e DATA_DIR=/data -e SITES="https://google.com,https://github.com" health-check-dashboard
```

---

## 🧪 CI/CD

Workflow file: `.github/workflows/ci-cd.yaml`

- **Test**:
  - `flake8` (lint)
  - `pytest` (basic unit tests)
  - `python -m compileall` (syntax check)
- **Build & Push**:
  - Docker build with `buildx`
  - Push to DockerHub (on `main`)
  - **Trivy scan** for vulnerabilities (CRITICAL/HIGH) – currently non-blocking (can be enforced)
- *(Optional)* Deploy step to Kubernetes

Secrets required:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

---

## 📈 Monitoring (Prometheus + Grafana)

The app exposes metrics at `/metrics`.  
Useful queries:
- `site_checks_total{site,status}`
- `site_response_time_seconds_bucket{site}`
- `histogram_quantile(0.95, sum(rate(site_response_time_seconds_bucket[5m])) by (le,site))`

For full monitoring:
1. Run Prometheus + Grafana (via Helm or Docker).
2. Configure Prometheus to scrape `http://<app>:5000/metrics`.
3. Import dashboards into Grafana.

---

## 📝 License
MIT — free to use with attribution.

---

## 🙋‍♂️ Credits
Built by Or-Ram Atar
