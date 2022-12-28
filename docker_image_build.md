# Build Docker Image for Database Migration Wave Orchestrator

Please find the list of steps required to build the docker image file.

### Clone Repo

Use GIT to clone repo

```
git clone https://github.com/GoogleCloudPlatform/database-migration-wave-orchestrator.git
```

Create a new folder where to build the container image

```
mkdir app
```

### Build Backend

Go to the backend directory and copy the files and folders.

```
cd backend
cp -fR -t ../app/ run.py bms_app bms-frontend-dev requirements.txt Dockerfile migrations
```
### Build Frontend
Go to the frontend directory and install teh node dependencies

```
cd frontend
npm run build
cp -fR -t ../app/bms-frontend-dev ./dist/bms-frontend-dev/*
```
## Build Container Image and Publish

Pre-Requisites: Docker, podman/buildah are used to complete this task.

```
cd ../app/
docker build --tag=<<<<GCP Container Registory Location>>>:latest .
docker push <<<<GCP Container Registory Location>>>:latest

###Clean up local image registry
docker rmi <<<<GCP Container Registory Location>>>:latest -f
```

