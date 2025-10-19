#!/bin/bash
set -e

# ========================================
# 2048 Game Kubernetes Installation Script
# ========================================

CLUSTER_NAME="cluster-local"
IMAGE_NAME="game-2048-image"
K8S_MANIFESTS_DIR="../k8s/manifests"
KIND_CONFIG_FILE="resources/kind-config.yaml"

echo "Starting 2048 Kubernetes deployment..."

# Step 1: Check required tools
for cmd in docker kind kubectl; do
  if ! command -v $cmd &>/dev/null; then
    echo "$cmd is not installed. Please install it first."
    exit 1
  fi
done

# Step 2: Create KIND cluster
echo "Creating KIND cluster..."
kind create cluster  --config $KIND_CONFIG_FILE

# Wait for KIND nodes to be Ready
echo "Waiting for KIND nodes to be Ready..."
for i in {1..12}; do
    NOT_READY=$(kubectl get nodes --no-headers | awk '{print $2}' | grep -v Ready || true)
    if [[ -z "$NOT_READY" ]]; then
        echo "All nodes are Ready!"
        break
    else
        echo "Waiting for nodes... ($i/12)"
        sleep 5
    fi
done

# Step 3: Build Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME ..

# Step 4: Load Docker image into KIND
echo "Loading Docker image into KIND..."
kind load docker-image $IMAGE_NAME --name $CLUSTER_NAME

# Step 5: Deploy NGINX Ingress Controller
echo "Deploying NGINX Ingress Controller..."
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml

# Wait for all ingress controller pods to be Ready
echo "Waiting for ingress controller pods..."
for i in {1..60}; do
    TOTAL=$(kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller --no-headers 2>/dev/null | wc -l)
    READY=$(kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller \
        -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null | grep -o true | wc -l)
    
    if [[ "$TOTAL" -gt 0 ]] && [[ "$TOTAL" == "$READY" ]]; then
        echo "All ingress controller pods are Ready!"
        break
    else
        echo "Waiting for ingress controller pods... ($i/60)"
        sleep 5
    fi

    if [[ "$i" == "60" ]]; then
        echo "Timeout waiting for ingress controller pods."
        kubectl get pods -n ingress-nginx
        exit 1
    fi
done

# Step 6: Add local host entry
echo "Adding local hosts entry for 2048.local..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo sh -c 'echo "127.0.0.1 2048.local" >> /etc/hosts'
else
    echo "Unsupported OS. Please add 127.0.0.1 2048.local to your hosts file manually."
fi

# Step 7: Deploy Kubernetes manifests
echo "Deploying application manifests..."
kubectl apply -f $K8S_MANIFESTS_DIR

# Wait for 2048 application pod(s) to be Ready
echo "Waiting for 2048 application pod(s)..."
for i in {1..60}; do
    TOTAL=$(kubectl get pods -l app=game-2048 --no-headers 2>/dev/null | wc -l)
    READY=$(kubectl get pods -l app=game-2048 \
        -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null | grep -o true | wc -l)
    
    if [[ "$TOTAL" -gt 0 ]] && [[ "$TOTAL" == "$READY" ]]; then
        echo "All application pods are Ready!"
        break
    else
        echo "Waiting for application pod(s)... ($i/60)"
        sleep 5
    fi

    if [[ "$i" == "60" ]]; then
        echo "Timeout waiting for application pod(s)."
        kubectl get pods
        exit 1
    fi
done

# Step 8: Show status
echo "Deployment completed!"
kubectl get pods,svc,ingress

echo "Open your browser at http://2048.local"
