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
