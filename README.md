# ShopSmart AI

A Python Flask e-commerce demo with a shopping assistant, TF-IDF product search, content-based recommendations, session cart, Docker, and Kubernetes manifests.

## Run locally (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

Copy `.env.example` to `.env` and add `OPENAI_API_KEY` to enable live AI responses. Without a key, the built-in catalog assistant works. Do not commit `.env`.

## Docker

```powershell
docker build -t shopsmart-ai:v1 .
docker run --rm -p 5000:5000 shopsmart-ai:v1
```

Open http://localhost:5000

## Kubernetes

Update `YOUR_ACR_NAME` in `k8s/deployment.yaml` to your Azure Container Registry name. Create the secret before applying the deployment:

```bash
kubectl create secret generic shopsmart-secrets --from-literal=secret-key='replace-with-a-long-random-value'
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
kubectl get service shopsmart-ai-service --watch
```

The service receives a public IP when the Azure LoadBalancer is provisioned.

## Important demo limitations

This starter uses SQLite and in-container storage for simplicity. For a production AKS deployment, move the database to a managed persistent database, store secrets in Azure Key Vault, configure persistent/shared cart storage, HTTPS, authentication, payment integration, monitoring, and backups. The sample does not process real payments or orders.
