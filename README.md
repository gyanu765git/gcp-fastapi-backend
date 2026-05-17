# FastAPI Health Check Service

A minimal FastAPI project with a single health check endpoint and Docker support.

## API

- `GET /health` — returns `{ "status": "healthy" }`

## Run locally

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Open the docs:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## Docker

Build and run with Docker:

```bash
docker build -t fastapi-healthcheck .
docker run -p 8000:8000 fastapi-healthcheck
```

Or with Docker Compose:

```bash
docker compose up --build
```

## GitHub Actions CI

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs on push and pull request to `main`.

The workflow performs:
- Python dependency install
- syntax validation with `python -m py_compile`
- a smoke test against `GET /health`
- Docker image build verification
- push the Docker image to Google Artifact Registry (when secrets are configured)

### Release flow

1. Make local changes and commit them.
2. Push to the remote `main` branch:
   ```bash
   git push origin main
   ```
3. Create a version tag locally:
   ```bash
   git tag v1.0.0
   ```
4. Push the tag:
   ```bash
   git push origin v1.0.0
   ```
5. GitHub Actions will build and push a tagged image to Artifact Registry.
6. Update `k8s/deployment.yaml` to point to the new image tag, then apply it to your cluster.

For example:
```bash
kubectl apply -f k8s/deployment.yaml
```

To enable Artifact Registry deployment, add these repository secrets in GitHub:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (service account JSON)
- `GCP_AR_LOCATION` (for example `us-central1`)
- `GCP_AR_REPOSITORY` (the Artifact Registry repo name)

## Deploy to GKE

1. Configure your GCP project and authenticate:
   ```bash
gcloud auth login
 gcloud config set project YOUR_PROJECT_ID
 gcloud auth configure-docker
```
2. Build and push the image:
   ```bash
docker build -t gcr.io/YOUR_PROJECT_ID/fastapi-healthcheck:latest .
docker push gcr.io/YOUR_PROJECT_ID/fastapi-healthcheck:latest
```

   Or use Artifact Registry:
   ```bash
gcloud artifacts repositories create fastapi-repo --repository-format=docker --location=us-central1
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-healthcheck:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-healthcheck:latest
```

   Then update `k8s/deployment.yaml` image to:
   `us-central1-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-healthcheck:latest`

3. Create or use an existing GKE cluster:
   ```bash
gcloud container clusters create fastapi-cluster --zone us-central1-a
 gcloud container clusters get-credentials fastapi-cluster --zone us-central1-a
```
4. Deploy Kubernetes resources:
   ```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
```

5. To use GKE Ingress, apply:
   ```bash
kubectl apply -f k8s/ingress.yaml
```

6. Check service / ingress status:
   ```bash
kubectl get svc fastapi-healthcheck-service
kubectl get ingress fastapi-healthcheck-ingress
```

6. Open the external IP in your browser, or use curl:
   ```bash
curl http://EXTERNAL_IP/health
```

7. Update the image when needed:
   ```bash
docker build -t gcr.io/YOUR_PROJECT_ID/fastapi-healthcheck:latest .
docker push gcr.io/YOUR_PROJECT_ID/fastapi-healthcheck:latest
kubectl rollout restart deployment/fastapi-healthcheck
```
