#!/usr/bin/env python3
import subprocess
import sys
import time
import platform

# ========================================
# 2048 Game Kubernetes Installation Script
# (Python version)
# ========================================

CLUSTER_NAME = "cluster-local"
IMAGE_NAME = "game-2048-image"
K8S_MANIFESTS_DIR = "../k8s/manifests"
KIND_CONFIG_FILE = "resources/kind-config.yaml"

def run(cmd, capture_output=False, check=True):
    """Helper to run shell commands"""
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        if capture_output:
            print(result.stdout)
            print(result.stderr)
        sys.exit(1)
    return result

def check_tools():
    for cmd in ["docker", "kind", "kubectl"]:
        if subprocess.run(f"command -v {cmd}", shell=True).returncode != 0:
            print(f"{cmd} is not installed. Please install it first.")
            sys.exit(1)

def wait_for_nodes_ready(timeout_sec=60):
    print("Waiting for KIND nodes to be ready...")
    for _ in range(timeout_sec // 5):
        result = subprocess.run(
            "kubectl get nodes --no-headers | awk '{print $2}' | grep -v Ready || true",
            shell=True, capture_output=True, text=True
        )
        if not result.stdout.strip():
            print("All KIND nodes are ready.")
            return
        time.sleep(5)
    print("Timeout waiting for KIND nodes.")
    run("kubectl get nodes")
    sys.exit(1)

def wait_for_pods(label_selector, namespace=None, timeout_sec=300):
    ns_flag = f"-n {namespace}" if namespace else ""
    print(f"Waiting for pod(s) with label '{label_selector}' in {namespace or 'default'} to become ready...")
    for _ in range(timeout_sec // 5):
        total_result = run(
            f"kubectl get pods {ns_flag} -l {label_selector} --no-headers 2>/dev/null | wc -l",
            capture_output=True
        )
        ready_result = run(
            f"kubectl get pods {ns_flag} -l {label_selector} -o jsonpath='{{.items[*].status.containerStatuses[*].ready}}' 2>/dev/null | grep -o true | wc -l",
            capture_output=True
        )
        total = int(total_result.stdout.strip())
        ready = int(ready_result.stdout.strip())
        print(f"Waiting for pod(s) to be ready: {ready}/{total}", end="\r")
        if total > 0 and total == ready:
            print(f"All pod(s) are ready! ({ready}/{total})")
            return
        time.sleep(5)
    print(f"\nTimeout waiting for pods {label_selector}")
    run(f"kubectl get pods {ns_flag}")
    sys.exit(1)

def add_host_entry():
    print("Adding local hosts entry for 2048.local...")
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        run('sudo sh -c \'echo "127.0.0.1 2048.local" >> /etc/hosts\'')
    else:
        print("Unsupported OS. Please add 127.0.0.1 2048.local to your hosts file manually.")

def main():
    print("Starting 2048 Kubernetes deployment...")

    check_tools()

    print("Creating KIND cluster...")
    run(f"kind create cluster --config {KIND_CONFIG_FILE}")

    wait_for_nodes_ready()

    print("Building Docker image...")
    run(f"docker build -t {IMAGE_NAME} ..")

    print("Loading Docker image into KIND...")
    run(f"kind load docker-image {IMAGE_NAME} --name {CLUSTER_NAME}")

    print("Deploying NGINX Ingress Controller...")
    run("kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml")

    wait_for_pods("app.kubernetes.io/component=controller", namespace="ingress-nginx")

    add_host_entry()

    print("Deploying application manifests...")
    run(f"kubectl apply -f {K8S_MANIFESTS_DIR}")

    wait_for_pods("app=game-2048")

    print("Deployment completed!")
    run("kubectl get pods,svc,ingress")

    print("Open your browser at http://2048.local")

if __name__ == "__main__":
    main()
