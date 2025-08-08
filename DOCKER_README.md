# LMS Platform - Docker Setup Guide

## Overview

This guide explains how to set up and run the LMS platform using Docker and Docker Compose. The platform consists of multiple microservices, a PostgreSQL database, Redis cache, and a React frontend.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │   PostgreSQL    │
│   (React)       │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
│   (Port 3000)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Microservices                          │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│  User Service   │ Course Service  │ Enrollment      │ Content │
│  (Port 8001)    │  (Port 8002)    │ Service         │ Service │
│                 │                 │ (Port 8003)     │(Port 8008)│
├─────────────────┼─────────────────┼─────────────────┼─────────┤
│ Assessment      │ Progress        │ Analytics       │ Comm.   │
│ Service         │ Service         │ Service         │ Service │
│ (Port 8004)     │ (Port 8005)     │ (Port 8006)     │(Port 8007)│
└─────────────────┴─────────────────┴─────────────────┴─────────┘
```

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd lms_project
```

### 2. Set Environment Variables

Copy the environment file and modify as needed:

```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 3. Build and Start Services

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Service Details

### Backend Services

| Service | Port | Description | Database |
|---------|------|-------------|----------|
| API Gateway | 8000 | Unified API entry point | - |
| User Service | 8001 | Authentication & user management | PostgreSQL |
| Course Service | 8002 | Course management | SQLite |
| Enrollment Service | 8003 | Course enrollments | PostgreSQL |
| Assessment Service | 8004 | Quizzes and exams | PostgreSQL |
| Progress Service | 8005 | Learning progress tracking | PostgreSQL |
| Analytics Service | 8006 | Analytics and reporting | PostgreSQL |
| Communication Service | 8007 | Messaging and notifications | PostgreSQL |
| Content Service | 8008 | File upload and management | SQLite |

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Caching and sessions |

## Environment Configuration

### Development Environment

For local development, use the `.env` file in the root directory:

```bash
# Database
POSTGRES_DB=lms_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
API_GATEWAY_URL=http://api-gateway:8000
USER_SERVICE_URL=http://user-service:8001
# ... other service URLs
```

### Production Environment

For production deployment, use the environment files in `k8s/env/`:

- `k8s/env/production.env` - Production settings
- `k8s/env/staging.env` - Staging settings
- `k8s/env/development.env` - Development settings

## Docker Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View running services
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api-gateway
```

### Development Operations

```bash
# Rebuild specific service
docker-compose build user-service

# Rebuild and restart specific service
docker-compose up -d --build user-service

# Execute command in running container
docker-compose exec user-service python manage.py shell

# Access database
docker-compose exec postgres psql -U lms_user -d lms_db
```

### Database Operations

```bash
# Create database backup
docker-compose exec postgres pg_dump -U lms_user lms_db > backup.sql

# Restore database from backup
docker-compose exec -T postgres psql -U lms_user -d lms_db < backup.sql

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

## Health Checks

All services include health checks. You can monitor service health:

```bash
# Check service health
docker-compose ps

# View health check logs
docker-compose logs | grep "health check"
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Change host port
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Service Startup Issues**
   ```bash
   # Check service logs
   docker-compose logs <service-name>
   
   # Rebuild service
   docker-compose build <service-name>
   docker-compose up -d <service-name>
   ```

### Debugging

```bash
# Access service container
docker-compose exec <service-name> bash

# Check service configuration
docker-compose config

# View resource usage
docker stats
```

## Performance Optimization

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  user-service:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Scaling Services

```bash
# Scale specific service
docker-compose up -d --scale user-service=3

# Scale multiple services
docker-compose up -d --scale user-service=2 --scale course-service=2
```

## Security Considerations

1. **Change Default Passwords**
   - Update database passwords in `.env`
   - Change JWT secret keys
   - Use strong passwords for all services

2. **Network Security**
   - Use internal networks for service communication
   - Expose only necessary ports
   - Implement proper firewall rules

3. **Container Security**
   - Run containers as non-root users
   - Keep base images updated
   - Scan images for vulnerabilities

## Monitoring and Logging

### Log Aggregation

```bash
# View all logs
docker-compose logs -f

# View logs with timestamps
docker-compose logs -f -t

# Export logs
docker-compose logs > logs.txt
```

### Metrics Collection

Enable metrics collection in environment variables:

```bash
METRICS_ENABLED=true
METRICS_PORT=9090
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U lms_user lms_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U lms_user -d lms_db < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v lms_project_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v lms_project_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## Production Deployment

For production deployment, consider:

1. **Use production environment variables**
2. **Enable SSL/TLS termination**
3. **Set up proper monitoring and alerting**
4. **Implement automated backups**
5. **Use container orchestration (Kubernetes)**

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs <service-name>`
3. Check GitHub issues
4. Contact the development team

## Contributing

When contributing to the Docker setup:

1. Test changes locally first
2. Update documentation
3. Follow the existing patterns
4. Add appropriate health checks
5. Include environment variable documentation 