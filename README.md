# <span style="color:#1ABD4E">2048 Game on Kubernetes</span> 🎮☸️

## <span style="color:#15993F">Project Purpose</span> 🌟

The goal of this project is to **containerize and deploy the classic 2048 web game** on a local Kubernetes cluster using **KIND (Kubernetes IN Docker)**.  

This project demonstrates how to:

- Run the classic 2048 web game by **building our own Docker image** from the forked repository [gabrielecirulli/2048](https://github.com/gabrielecirulli/2048) and **writing our own Dockerfile**.
- Deploy it with **Kubernetes manifests** or **Helm**.
- Expose the application via **Ingress** for browser access.
- Run a **local Kubernetes cluster** easily using KIND.

By the end, you will be able to open your browser at `http://2048.local` and play the game directly from your local Kubernetes environment.

## <span style="color:#15993F">Prerequisites </span> 📋

Before starting, make sure you have the following installed on your machine:

- **Docker** – to run KIND nodes and build the Docker image. (Docker Desktop can be used.)
- **KIND** – to create a local Kubernetes cluster.
- **kubectl** – to interact with the Kubernetes cluster.
- **Helm** – to deploy the 2048 game via the Helm chart. (Optional for Helm installation)
- **Git** – to clone this repository.
- **A web browser** – to access the game at `http://2048.local`.

## <span style="color:#15993F">Step-by-Step Installation</span> 🛠️

### <span style="color:#128236">Step 1: Clone the repository</span>
Clone this repository to your local machine:

```bash
git clone https://github.com/kadirariklar/game-2048-for-k8s.git
cd game-2048-for-k8s
```


### <span style="color:#128236">Step 2: Create a KIND Cluster</span>
Create a KIND cluster

> **Note:** For the Ingress controller we will set up later, the `extraPortMappings` parameter needs to be added for the worker node in the `kind-config.yaml` to expose the service externally without using `kubectl port-forward` or NodePort.
 

The cluster has been created with **one master and one worker node**.  
If a different cluster configuration is desired, the `kind-config.yaml` can be edited accordingly.


```bash
cd k8s # Navigate to the k8s folder
kind create cluster --config kind-config.yaml
```

Verify the nodes:

Check that all nodes are ready:

```bash
kubectl get nodes


#You should see output similar to:

NAME                           STATUS   ROLES           AGE   VERSION
cluster-local-control-plane    Ready    control-plane   1m    v1.34.0
cluster-local-worker           Ready    <none>          1m    v1.34.0

# Make sure all nodes have "STATUS: Ready" before proceeding.
```

### <span style="color:#128236">Step 3: Build Docker Image and Load into KIND Cluster</span>
Build the Docker image using the provided Dockerfile and make it available to the KIND cluster:

```bash
# Build the Docker image
cd ../2048-game/  # Navigate to the folder containing the Dockerfile and 2048 game files.
docker build -t game-2048-image .

# Load the image into the KIND cluster so it can be used by the deployments.

# Make sure to set the --name parameter to match your KIND cluster name (e.g., cluster-local)

kind load docker-image game-2048-image --name cluster-local

# Note: The --name parameter must match the name of your KIND cluster (cluster-local in this setup), otherwise the cluster will not see the image and your pods may fail with ImagePullBackOff.

```
Note: The --name parameter must match the name of your KIND cluster (cluster-local in this setup), otherwise the cluster will not see the image and your pods may fail with ImagePullBackOff.

### <span style="color:#128236">Step 4: Deploy NGINX Ingress Controller</span>

To make your 2048 web app accessible via a hostname (e.g., `2048.local`), this project uses an **Ingress controller (NGINX)** to expose the Service outside the cluster.
 
We will deploy the **NGINX Ingress Controller** to handle incoming HTTP requests and route them to the application service.

Deploy the controller using the following command:

```bash
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml

# Check that the Ingress pods are running:

kubectl get pods -n ingress-nginx

# You should see output similar to:

NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-controller-xxxxxxxxxx-xxxxx   1/1     Running     0          1m
ingress-nginx-admission-create-xxxxx        0/1     Completed   0          1m
ingress-nginx-admission-patch-xxxxx         0/1     Completed   0          1m

# Check that the Ingress class exists:

kubectl get ingressclass

Expected output:

NAME    CONTROLLER
nginx   k8s.io/ingress-nginx

# Make sure the controller pod is Running and the Ingress class (nginx) exists before proceeding.
```

### <span style="color:#128236">Step 5: Add Local Host Entry</span> 

To access your 2048 web app via the hostname `2048.local` in your browser, you need to map this hostname to `127.0.0.1` in your system's hosts file. This ensures that requests to `2048.local` are routed to your local KIND cluster.

**On macOS and Linux:**

```bash
sudo sh -c 'echo "127.0.0.1 2048.local" >> /etc/hosts'
```

**On Windows OS:**

Open the hosts file as Administrator located at:

```bash
C:\Windows\System32\drivers\etc\hosts
```

Add the following line at the end of the file:

```bash
127.0.0.1 2048.local
```

Save the file.

### <span style="color:#128236">Step 6: Deploy the 2048 Application and Access It</span>  

Navigate to the `Manifests` folder where your Kubernetes manifests are located:

```bash
cd ../k8s/manifests # Navigate to the manifest folder containing k8s manifest not Helm templates.

# Deploy the application, service, and ingress:

kubectl apply -f .

# Verify that the pods are running:

kubectl get pods,svc,ingress

# Expected output:

NAME                                READY   STATUS    RESTARTS   AGE
pod/game-2048-xxxxxxxxxx-xxxxx      1/1     Running   0          1m

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
svc/game-2048        ClusterIP   10.96.x.x      <none>        80/TCP    1m
svc/kubernetes       ClusterIP   10.96.x.x      <none>        443/TCP   10m

NAME                                          CLASS   HOSTS        ADDRESS   PORTS   AGE
ingress.networking.k8s.io/game-2048-ingress   nginx   2048.local   localhost 80      1m

# Once all pods are Running and services/ingress are active, open your browser and navigate to:
```
<a>http://2048.local</a>


**You should see the classic 2048 game running.**

<hr>

### <span style="color:#8CA4BD">Deploy with Helm (Optional)</span>

Before Helm installation, it is recommended to run **kubectl delete -f .** in the same directory (/k8s/manifests) to remove any previously applied Kubernetes manifests.

```bash
# Navigate to the Helm chart directory:

cd ../helm-2048

# Install the Helm chart:

helm install game-2048 .

kubectl get pods,svc,ingress

# Expected output:

NAME                                  READY   STATUS    RESTARTS   AGE
pod/game-2048-xxxxxxxxxx-xxxxx        1/1     Running   0          1m

NAME                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
service/game-2048        ClusterIP   10.96.123.45     <none>        80/TCP    1m

NAME                             CLASS   HOSTS         ADDRESS   PORTS   AGE
ingress.networking.k8s.io/2048   nginx   2048.local    localhost 80      1m

# Once all pods are in the Running state, open your browser and visit:

👉 http://2048.local

You should see the classic 2048 game running.

# To uninstall the release, use the following command:

helm uninstall game-2048

```

### 🧹 Delete KIND Cluster

If you want to remove your KIND cluster after completing all steps, you can safely delete it.  
This will remove all resources and containers created by KIND, freeing up system resources.

```bash
kind delete cluster --name cluster-local
```

<hr>
<hr>

## 🔀 Traffic Flow Overview

![alt text](<Traffic Flow.png>)



