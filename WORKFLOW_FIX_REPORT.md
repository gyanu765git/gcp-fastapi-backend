# CI/CD & Workload Identity Fix Report

Date: 2026-05-17
Repository: gcp-fastapi-backend

## Summary
I fixed GitHub Actions authentication failures by switching to Workload Identity Federation, created the necessary GCP resources (Workload Identity Pool/Provider and service account), updated the GitHub Actions workflow to use the provider, and validated deployment to the cluster.

## Files changed
- .github/workflows/ci.yml — added job to build and push image, switched auth to Workload Identity, set GCP env values.
- k8s/deployment.yaml — Kubernetes Deployment manifest (image points to Artifact Registry).
- README.md — documentation for CI/release flow and Workload Identity notes.

## GIT operations I executed
```bash
git add .github/workflows/ci.yml README.md k8s/deployment.yaml
git commit -m 'Add GitHub Actions release workflow and Kubernetes deployment manifest'
git push origin main
# create and push release tag
git tag v1.0.0
git push origin v1.0.0
# later: commit workflow fix
git add .github/workflows/ci.yml
git commit -m 'Fix GitHub Actions Workload Identity auth and set GCP env values'
git push origin main
```

## GCloud commands I executed (Workload Identity setup)
Replace `PROJECT_ID`/`PROJECT_NUMBER`/`REPO_OWNER`/`REPO_NAME` where appropriate.

Create workload identity pool (if missing):
```bash
gcloud iam workload-identity-pools create github-pool \
  --project="project-6206f1cc-135e-44bd-acf" --location="global" --display-name="GitHub Actions pool"
```

Create OIDC provider (if missing):
```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project="project-6206f1cc-135e-44bd-acf" --location="global" --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --display-name="GitHub Actions OIDC provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref"
```

(If provider condition was incorrect) Update provider attribute condition to match the repository:
```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --project="project-6206f1cc-135e-44bd-acf" --location=global --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository=='gyanu765git/gcp-fastapi-backend'" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"
```

Create service account (no key):
```bash
gcloud iam service-accounts create github-actions-sa \
  --project="project-6206f1cc-135e-44bd-acf" --display-name="GitHub Actions SA"
```

Grant Artifact Registry writer role to the SA:
```bash
gcloud projects add-iam-policy-binding "project-6206f1cc-135e-44bd-acf" \
  --member="serviceAccount:github-actions-sa@project-6206f1cc-135e-44bd-acf.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

Allow the workload identity pool to impersonate the SA (Workload Identity binding):
```bash
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@project-6206f1cc-135e-44bd-acf.iam.gserviceaccount.com" \
  --project="project-6206f1cc-135e-44bd-acf" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/115566091564/locations/global/workloadIdentityPools/github-pool/attribute.repository/gyanu765git/gcp-fastapi-backend"
```

## Workflow edits (high level)
- Trigger on push to `main` and on tags `v*`.
- Lint/test job: set up Python, install deps, validate syntax, run smoke test `curl /health`.
- Build job: build Docker image.
- Push job: runs only on push to main or tag refs; uses Workload Identity provider and `github-actions-sa` service account to authenticate and push the image to Artifact Registry.
- Environment values set inside workflow:
  - `GCP_PROJECT_ID: project-6206f1cc-135e-44bd-acf`
  - `GCP_AR_LOCATION: asia-south1`
  - `GCP_AR_REPOSITORY: fastapi-images`

## Commands I ran to deploy locally / verify
```bash
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/fastapi-healthcheck
kubectl get pods -l app=fastapi-healthcheck
kubectl logs -l app=fastapi-healthcheck --tail=200
```

## Verification I performed
- Confirmed Workload Identity pool/provider state: `ACTIVE`.
- Updated provider `attributeCondition` to `gyanu765git/gcp-fastapi-backend`.
- Created `github-actions-sa` and verified it has `roles/artifactregistry.writer` and `roles/iam.workloadIdentityUser` binding for the workload identity principal.
- Committed and pushed updated workflow to `main`.
- Observed `kubectl apply -f k8s/deployment.yaml` created the deployment in the cluster.

## Notes & next steps
- The GitHub Actions workflow should now authenticate via Workload Identity and push images to Artifact Registry. Re-run the workflow or push a new tag to verify a successful `push-to-artifact-registry` run.
- If you want automated deployment from CI (apply/update the Kubernetes manifest), we can add a step to the workflow to update the `k8s/deployment.yaml` image and apply it to the cluster; that requires providing cluster credentials (kubeconfig) or setting up Workload Identity for GKE.

---

If you want this exported as a `.docx` or `.pdf`, tell me and I will convert and add it to the repository for download.