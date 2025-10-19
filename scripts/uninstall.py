#!/usr/bin/env python3
import subprocess
import sys
import platform

# ========================================
# 2048 Game Kubernetes Uninstall Script (Python)
# ========================================

CLUSTER_NAME = "cluster-local"
IMAGE_NAME = "game-2048-image"
HOST_ENTRY = "2048.local"

print("Starting 2048 Kubernetes uninstall...")

# Step 1: Delete KIND cluster
print(f"Deleting KIND cluster: {CLUSTER_NAME}...")
try:
    clusters = subprocess.check_output(["kind", "get", "clusters"], text=True).splitlines()
    if CLUSTER_NAME in clusters:
        subprocess.run(["kind", "delete", "cluster", "--name", CLUSTER_NAME], check=True)
        print("KIND cluster deleted.")
    else:
        print(f"KIND cluster '{CLUSTER_NAME}' not found. Skipping.")
except FileNotFoundError:
    print("kind command not found. Please install KIND.")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"Error deleting KIND cluster: {e}")
    sys.exit(1)

# Step 2: Remove Docker image
print(f"Removing Docker image: {IMAGE_NAME}...")
try:
    images = subprocess.check_output(["docker", "images", "-q", IMAGE_NAME], text=True).strip()
    if images:
        subprocess.run(["docker", "rmi", IMAGE_NAME], check=False)
        print("Docker image removed.")
    else:
        print(f"Docker image '{IMAGE_NAME}' not found. Skipping.")
except FileNotFoundError:
    print("docker command not found. Please install Docker.")
    sys.exit(1)

# Step 3: Clean /etc/hosts entry
print(f"Cleaning /etc/hosts entry for {HOST_ENTRY}...")
system = platform.system()
try:
    if system == "Darwin":
        subprocess.run(["sudo", "sed", "-i", "", f"/{HOST_ENTRY}/d", "/etc/hosts"], check=True)
        print("Hosts entry removed (Mac).")
    elif system == "Linux":
        subprocess.run(["sudo", "sed", "-i", f"/{HOST_ENTRY}/d", "/etc/hosts"], check=True)
        print("Hosts entry removed (Linux).")
    else:
        print(f"Unsupported OS ({system}). Please remove the entry for {HOST_ENTRY} manually.")
except subprocess.CalledProcessError as e:
    print(f"Error cleaning hosts file: {e}")
    sys.exit(1)

print("2048 Kubernetes uninstall completed!")
