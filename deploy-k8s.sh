#!/bin/bash
# Grimoire Kubernetes Deployment Script

set -e

echo "🧙 Grimoire Chatroom - Kubernetes Deployment"
echo "==========================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

# Parse arguments
NAMESPACE=${1:-grimoire}
ACTION=${2:-deploy}

case $ACTION in
    deploy)
        echo "📦 Deploying Grimoire to namespace: $NAMESPACE"
        echo ""
        
        # Create namespace
        echo "1️⃣  Creating namespace..."
        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
        
        # Apply secrets
        echo "2️⃣  Applying secrets..."
        kubectl apply -f k8s/secret.yaml
        
        # Deploy PostgreSQL
        echo "3️⃣  Deploying PostgreSQL..."
        kubectl apply -f k8s/postgres-deployment.yaml
        
        echo "   Waiting for PostgreSQL to be ready (30 seconds)..."
        sleep 30
        
        # Deploy Flask app
        echo "4️⃣  Deploying Flask application..."
        kubectl apply -f k8s/app-deployment.yaml
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "📊 Checking pod status..."
        kubectl get pods -n $NAMESPACE
        echo ""
        echo "🌐 To access the application:"
        echo "   kubectl port-forward -n $NAMESPACE svc/web 5000:5000"
        echo "   Then visit: http://localhost:5000"
        ;;
        
    delete)
        echo "🗑️  Deleting Grimoire from namespace: $NAMESPACE"
        kubectl delete namespace $NAMESPACE --ignore-not-found
        echo "✅ Deletion complete!"
        ;;
        
    logs)
        echo "📋 Showing logs for Flask app..."
        kubectl logs -n $NAMESPACE -l app=web --tail=50 -f
        ;;
        
    logs-db)
        echo "📋 Showing logs for PostgreSQL..."
        kubectl logs -n $NAMESPACE -l app=postgres --tail=50 -f
        ;;
        
    status)
        echo "📊 Deployment status for namespace: $NAMESPACE"
        echo ""
        echo "Pods:"
        kubectl get pods -n $NAMESPACE
        echo ""
        echo "Services:"
        kubectl get svc -n $NAMESPACE
        echo ""
        echo "Events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
        ;;
        
    scale)
        REPLICAS=${3:-3}
        echo "📈 Scaling Flask app to $REPLICAS replicas..."
        kubectl scale deployment web -n $NAMESPACE --replicas=$REPLICAS
        echo "✅ Scaled!"
        ;;
        
    describe)
        echo "🔍 Describing deployments..."
        kubectl describe deployment -n $NAMESPACE
        ;;
        
    *)
        echo "Usage: $0 [namespace] [action] [args]"
        echo ""
        echo "Actions:"
        echo "  deploy      - Deploy the entire application (default)"
        echo "  delete      - Delete the entire application"
        echo "  logs        - Show Flask app logs"
        echo "  logs-db     - Show PostgreSQL logs"
        echo "  status      - Show deployment status"
        echo "  scale N     - Scale Flask app to N replicas"
        echo "  describe    - Describe all deployments"
        echo ""
        echo "Examples:"
        echo "  $0 grimoire deploy"
        echo "  $0 grimoire logs"
        echo "  $0 grimoire scale 3"
        exit 1
        ;;
esac
