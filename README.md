# Learning Management System (LMS)

This repository contains a microservice‑based implementation of a Learning Management System (LMS) built with **FastAPI** for the backend services and **React** for the frontend.  Each service is packaged as its own container and can be deployed independently to a Kubernetes cluster.  The structure of this repository closely follows the product requirements document.

## Repository Structure

```
lms_project/
├── backend/                # All Python microservices
│   ├── user_service/       # User management microservice
│   ├── course_service/     # Course CRUD microservice
│   ├── enrollment_service/ # Enrollment tracking microservice
│   ├── content_service/    # Content upload and retrieval microservice
│   ├── assessment_service/ # Quiz and assessment microservice
│   ├── progress_service/   # User progress tracking microservice
│   ├── communication_service/ # Messaging/announcements microservice
│   └── analytics_service/  # Analytics and reporting microservice
└── frontend/               # React application for students, instructors and admins
```

Each backend service has the following layout:

```
service_name/
├── app/
│   ├── main.py       # FastAPI application
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Pydantic schemas
│   ├── crud.py       # Database operations
│   └── database.py   # Async database session
├── requirements.txt  # Python dependencies
├── Dockerfile        # Build definition for container image
└── k8s/
    ├── deployment.yaml # Kubernetes Deployment manifest
    └── service.yaml    # Kubernetes Service manifest
```

The React frontend is intentionally lightweight here – it demonstrates how to structure pages and interact with the microservices.  In a real‑world deployment you would expand on these components, add proper state management (e.g. Redux or React Context), routing and authentication.

## Getting Started

The microservices can be run locally with Python and uvicorn.  Each service reads its database URL from the `DATABASE_URL` environment variable; by default they point at local PostgreSQL databases.

1. Install PostgreSQL and create the necessary databases for each service (`user_db`, `course_db`, `enrollment_db`, etc.).  Update the `DATABASE_URL` in each service or set the environment variable when running.
2. Navigate to a service directory and install dependencies:

   ```bash
   cd backend/user_service
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Access the service at `http://localhost:8000`.  Each service exposes its own API endpoints under `/api/v1/…`.

For Docker/Kubernetes, build the images and apply the manifests from the `k8s/` folders.  Be sure to create the corresponding PostgreSQL instances and configure environment variables for each deployment.
