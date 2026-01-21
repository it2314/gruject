# Grimoire Chatroom - Kubernetes Deployment Guide

## Overview

This is a Flask-based chatroom application designed to run on Kubernetes with PostgreSQL backend. The application features a mystical themed message board where users can post and view messages.

## Features

- 📝 Post messages to the grimoire
- 📖 View all messages in the chatroom
- 🎨 Fantasy-themed UI with animated effects
- 🗄️ PostgreSQL database for persistence
- ☸️ Kubernetes-ready with health checks and resource limits
- 🔐 Secret-based configuration management

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip

### Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export DATABASE_URL="postgresql://pguser:pgpass@localhost:5432/grimoire_db"
export SECRET_KEY="your-secret-key-here"
```

5. Run the application:
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Docker Build

```bash
docker build -t flask-wtforms-example:latest .
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker registry access (for custom images)

### Deployment Steps

#### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

#### 2. Update Secrets (IMPORTANT - Production)
Edit `k8s/secret.yaml` and change all values:
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Strong password (min 16 chars)
- `POSTGRES_DB`: Database name
- `SECRET_KEY`: Random secret (min 32 chars)

```bash
# Generate a secure secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

Then apply:
```bash
kubectl apply -f k8s/secret.yaml
```

#### 3. Deploy PostgreSQL
```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

Verify PostgreSQL is running:
```bash
kubectl get pods -n grimoire -l app=postgres
kubectl logs -n grimoire -l app=postgres
```

#### 4. Deploy Flask App
First, make sure your Docker image is accessible to the cluster:
```bash
# If using local Docker
docker tag flask-wtforms-example:latest flask-wtforms-example:latest

# Push to registry (if required)
docker push <registry>/flask-wtforms-example:latest
```

Then deploy:
```bash
kubectl apply -f k8s/app-deployment.yaml
```

#### 5. Verify Deployment
```bash
# Check pods
kubectl get pods -n grimoire

# Check services
kubectl get svc -n grimoire

# View app logs
kubectl logs -n grimoire -l app=web --tail=100 -f
```

#### 6. Access the Application

**Port Forward (Local Access):**
```bash
kubectl port-forward -n grimoire svc/web 5000:5000
```
Visit: `http://localhost:5000`

**Ingress (Production):**
See `k8s/namespace.yaml` for Ingress setup. Update hostname and configure cert-manager.

### Database Initialization

The app automatically creates tables on first request. To manually initialize:

```bash
kubectl exec -it -n grimoire deployment/web -- python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Kubernetes Architecture

```
┌─────────────────────────────────┐
│     Kubernetes Cluster          │
│  ┌──────────────────────────┐   │
│  │   Namespace: grimoire    │   │
│  │                          │   │
│  │  ┌────────────────────┐  │   │
│  │  │  Web Service       │  │   │
│  │  │  (ClusterIP)       │  │   │
│  │  │  Port: 5000        │  │   │
│  │  │                    │  │   │
│  │  │  ┌──────────────┐  │  │   │
│  │  │  │ Flask Pod 1  │  │  │   │
│  │  │  │ Flask Pod 2  │  │  │   │
│  │  │  └──────────────┘  │  │   │
│  │  └────────────────────┘  │   │
│  │                          │   │
│  │  ┌────────────────────┐  │   │
│  │  │  Postgres Service  │  │   │
│  │  │  (ClusterIP)       │  │   │
│  │  │  Port: 5432        │  │   │
│  │  │                    │  │   │
│  │  │  ┌──────────────┐  │  │   │
│  │  │  │ Postgres Pod │  │  │   │
│  │  │  │ (PVC: 5Gi)   │  │  │   │
│  │  │  └──────────────┘  │  │   │
│  │  └────────────────────┘  │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

## Health Checks

Both apps have configured liveness and readiness probes:

- **Liveness Probe**: Ensures pod is still running
- **Readiness Probe**: Ensures pod is ready to serve traffic

Check probe status:
```bash
kubectl describe pod -n grimoire <pod-name>
```

## Scaling

Scale the Flask deployment:
```bash
kubectl scale deployment web -n grimoire --replicas=3
```

## Monitoring

### Logs
```bash
# Flask app logs
kubectl logs -n grimoire -l app=web -f

# PostgreSQL logs
kubectl logs -n grimoire -l app=postgres -f

# Follow logs from specific pod
kubectl logs -n grimoire <pod-name> -f
```

### Resource Usage
```bash
kubectl top pods -n grimoire
kubectl top nodes
```

### Events
```bash
kubectl get events -n grimoire --sort-by='.lastTimestamp'
```

## Troubleshooting

### Pod Won't Start
```bash
# Check pod status
kubectl describe pod -n grimoire <pod-name>

# Check logs
kubectl logs -n grimoire <pod-name>
```

### Database Connection Issues
```bash
# Test PostgreSQL connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h postgres -U pguser -d grimoire_db -c "SELECT 1"
```

### Recreate Everything
```bash
kubectl delete namespace grimoire
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/app-deployment.yaml
```

## Production Checklist

- [ ] Update all secrets in `k8s/secret.yaml`
- [ ] Configure Ingress domain and SSL certificates
- [ ] Set up PersistentVolume for PostgreSQL
- [ ] Configure resource requests/limits appropriately
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy for database
- [ ] Set up horizontal pod autoscaling
- [ ] Configure network policies
- [ ] Use a proper container registry
- [ ] Implement CI/CD pipeline

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `postgres` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | - | PostgreSQL username (from secret) |
| `POSTGRES_PASSWORD` | - | PostgreSQL password (from secret) |
| `POSTGRES_DB` | - | Database name (from secret) |
| `SECRET_KEY` | - | Flask secret key (from secret) |
| `DATABASE_URL` | Auto-built | Full database URL (optional override) |

## License

MIT
