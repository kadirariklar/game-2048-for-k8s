#!/bin/bash
set -e

# ========================================
# 2048 Game Kubernetes Uninstall Script
# ========================================
# This script deletes the KIND cluster, removes the Docker image,
# and cleans up the /etc/hosts entry for 2048.local.
# ========================================

# Variables
CLUSTER_NAME="cluster-local"
IMAGE_NAME="game-2048-image"
HOST_ENTRY="2048.local"

echo "Starting 2048 Kubernetes uninstall..."

# Step 1: Delete KIND cluster
echo "Deleting KIND cluster: $CLUSTER_NAME..."
if kind get clusters | grep -q "$CLUSTER_NAME"; then
    kind delete cluster --name $CLUSTER_NAME
    echo "KIND cluster deleted."
else
    echo "KIND cluster '$CLUSTER_NAME' not found. Skipping."
fi

# Step 2: Remove Docker image
echo "Removing Docker image: $IMAGE_NAME..."
if docker images -q $IMAGE_NAME > /dev/null; then
    docker rmi $IMAGE_NAME || echo "Failed to remove Docker image, it may not exist."
    echo "Docker image removed."
else
    echo "Docker image '$IMAGE_NAME' not found. Skipping."
fi

# Step 3: Clean /etc/hosts entry
echo "Cleaning /etc/hosts entry for $HOST_ENTRY..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo sed -i '' "/$HOST_ENTRY/d" /etc/hosts
    echo "Hosts entry removed (Mac)."
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo sed -i "/$HOST_ENTRY/d" /etc/hosts
    echo "Hosts entry removed (Linux)."
else
    echo "Unsupported OS. Please remove the entry for $HOST_ENTRY manually."
fi

echo "2048 Kubernetes uninstall completed!"
