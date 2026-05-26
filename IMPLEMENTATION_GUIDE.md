# Civifix Complaint Management Module - Implementation Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Component Details](#component-details)
4. [API Integration](#api-integration)
5. [Deployment Guide](#deployment-guide)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB 5.0+
- Docker (optional)

### Installation

```bash
# Clone repository
git clone <repo>
cd civifix-backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Configure environment variables
# Edit .env with your MongoDB URL and settings
```

### Running the Application

```bash
# Development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

# Docker
docker-compose up -d
```

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Access API documentation
# Swagger UI: http://localhost:8000/api/docs
# ReDoc: http://localhost:8000/api/redoc
```

## 🏗️ Architecture Overview

### Three-Layer Clean Architecture

```
┌─────────────────────────────────────┐
│      API Routes (FastAPI)           │
│  wards_routes.py                    │
│  complaints_routes.py               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Service Layer                  │
│  ward_service.py                    │
│  complaint_service.py               │
│  notification_service.py            │
│  file_upload_service.py             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Repository Layer               │
│  ward_repository.py                 │
│  complaint_repository.py            │
│  notification_repository.py         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      MongoDB Database               │
│  complaints collection              │
│  complaint_history collection       │
│  wards collection                   │
│  notifications collection           │
└─────────────────────────────────────┘
```

### Complaint Lifecycle State Machine

```
┌──────────┐
│   OPEN   │ ← Citizen creates complaint
└────┬─────┘
     │ Inspector assigns worker
     ↓
┌──────────┐
│ WORKING  │ ← Worker executes task
└────┬─────┘
     │ Worker submits work
     ↓
┌──────────────┐
│  APPROVAL    │ ← Inspector reviews
└────┬─────────┘
     ├──► CLOSED (Inspector approves)
     │
     └──► WORKING (Inspector rejects with reason)
```

## 📦 Component Details

### 1. Models (`app/models/`)

**complaint_model.py**
- `complaint_document()`: Creates complaint MongoDB document
- `complaint_history_document()`: Creates audit trail entry
- `complaint_response()`: Formats response

**ward_model.py**
- `ward_document()`: Creates ward MongoDB document

**district_model.py**
- `district_document()`: Creates district MongoDB document

**notification_model.py**
- `notification_document()`: Creates notification record

### 2. Repositories (`app/repositories/`)

**ComplaintRepository**
```python
# Key methods
create()                    # Insert new complaint
get_by_id()                # Fetch complaint by MongoDB ID
get_by_complaint_id()      # Fetch by complaint number
update()                   # Update complaint fields
get_recent_by_user()       # Get user's recent complaints
get_by_ward()              # Get all ward complaints
get_by_inspector()         # Get assigned complaints
get_by_worker()            # Get worker tasks
search()                   # Search with filters
add_history()              # Add audit trail entry
get_history()              # Get complaint history
count_by_user_this_week()  # Check weekly limit
count_by_user_today()      # Check daily limit
get_with_duplicates()      # Find potential duplicates
```

**WardRepository**
```python
# Key methods
create()                   # Create new ward
get_by_id()               # Fetch ward
get_by_ward_number()      # Fetch by ward number
update()                  # Update ward
list_by_district()        # List with pagination
list_by_inspector()       # Inspector's wards
search()                  # Search by name/number
update_complaint_counts() # Update complaint statistics
```

**NotificationRepository**
```python
# Key methods
create()                  # Create notification
get_user_notifications()  # Get user's notifications
mark_as_sent()           # Update status to sent
mark_as_delivered()      # Update status to delivered
get_pending_notifications() # Get unprocessed notifications
```

### 3. Services (`app/services/`)

**ComplaintService**
```python
# Key methods
create_complaint()         # Create with all validations
get_complaint()           # Get with history
assign_worker()           # Assign worker to task
submit_work()             # Worker submits completion
approve_complaint()       # Inspector approves
reject_complaint()        # Inspector rejects
get_user_complaints()     # Get citizen's complaints
get_ward_complaints()     # Get ward's complaints
get_inspector_dashboard() # Dashboard statistics
```

**WardService**
```python
# Key methods
create_ward()            # Create with validations
update_ward()            # Update ward
get_ward()              # Get details
list_wards()            # List with pagination
search_wards()          # Search functionality
deactivate_ward()       # Deactivate ward
```

**NotificationService**
```python
# Key methods
notify_complaint_created()      # Notify inspector
notify_worker_assigned()        # Notify worker
notify_work_submitted()         # Notify inspector
notify_complaint_approved()     # Notify citizen & worker
notify_complaint_rejected()     # Notify worker
```

**FileUploadService**
```python
# Key methods
validate_file()                  # Validate file type & size
upload_to_s3()                  # Upload to AWS S3
upload_to_minio()               # Upload to MinIO
upload_complaint_image()        # Upload with naming
compress_image()                # Compress for optimization
delete_file()                   # Remove from storage
```

### 4. Validators (`app/utils/`)

**ComplaintValidator**
```python
validate_gps_coordinates()      # Check lat/lon ranges
validate_description()          # Check length & content
validate_email()               # Email format
validate_phone()               # Indian phone format
validate_image_urls()          # URL and count validation
validate_priority()            # Check valid priority
validate_complaint_type()      # Check complaint type
```

**DuplicateComplaintDetector**
```python
calculate_distance()           # Haversine formula
is_duplicate()                # Check for duplicates
```

**SpamDetector**
```python
check_weekly_limit()          # Max 2 per week
check_daily_limit()           # Max 1 per day
check_repetitive_descriptions() # Jaccard similarity check
```

## 🔌 API Integration

### Authentication Flow
1. User registers/logs in via `/api/v1/auth/register`
2. Receives JWT token
3. Includes token in `Authorization: Bearer <token>` header
4. Token verified by `get_current_user()` dependency

### Example Integration

```python
# Get complaint with auth
curl -H "Authorization: Bearer eyJhbGc..." \
     http://localhost:8000/api/v1/complaints/507f1f77bcf86cd799439012

# Create complaint
curl -X POST http://localhost:8000/api/v1/complaints \
     -H "Authorization: Bearer eyJhbGc..." \
     -H "Content-Type: application/json" \
     -d '{
       "ward_id": "507f1f77bcf86cd799439011",
       "complaint_type": "GARBAGE",
       "description": "Garbage pile...",
       "latitude": 13.0827,
       "longitude": 80.2707
     }'
```

### RBAC Implementation

```python
# Role-based decorators
@router.post("", dependencies=[Depends(lambda: verify_role(["CITIZEN"]))])
async def create_complaint(...):
    # Only accessible to CITIZEN role
    pass

@router.put("/{id}/approve", dependencies=[Depends(lambda: verify_role(["INSPECTOR"]))])
async def approve_complaint(...):
    # Only accessible to INSPECTOR role
    pass
```

## 📊 Database Indexes

Critical indexes created automatically on startup:

```javascript
// Complaints
db.complaints.createIndex({ "complaint_id": 1 }, { unique: true })
db.complaints.createIndex({ "user_id": 1, "created_at": -1 })
db.complaints.createIndex({ "status": 1, "created_at": -1 })
db.complaints.createIndex({ "ward_id": 1, "status": 1 })

// Wards
db.wards.createIndex({ "district_id": 1, "ward_number": 1 }, { unique: true })
db.wards.createIndex({ "inspector_id": 1 })

// Performance optimization
db.complaints.createIndex({ "location": "2dsphere" })  // Geospatial
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
pytest app/tests/ -v

# Run specific test file
pytest app/tests/test_complaints.py -v

# Run with coverage
pytest app/tests/ --cov=app --cov-report=html
```

### Test Categories
- **Validator Tests**: GPS, email, phone, description validation
- **Duplicate Detection Tests**: Location-based and type-based
- **Spam Detection Tests**: Weekly/daily limits
- **Service Tests**: Business logic with mocked repositories
- **API Tests**: Endpoint integration tests

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t civifix-backend:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Environment Configuration

Create `.env`:
```
# Database
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=civifix

# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Application
ENV=production
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["https://example.com", "https://admin.example.com"]

# File Upload (optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=civifix-complaints

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### AWS S3 Setup

```bash
# Create S3 bucket
aws s3 mb s3://civifix-complaints --region us-east-1

# Create IAM user with S3 access
# Download credentials and configure

# Set bucket permissions
aws s3api put-bucket-cors \
  --bucket civifix-complaints \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }]
  }'
```

### Kubernetes Deployment (Optional)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civifix-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: civifix-backend
  template:
    metadata:
      labels:
        app: civifix-backend
    spec:
      containers:
      - name: backend
        image: civifix-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: civifix-secrets
              key: mongodb-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## 🐛 Troubleshooting

### Common Issues

#### "Ward not found"
- Check ward_id is valid ObjectId
- Verify ward exists: `db.wards.findOne({_id: ObjectId("...")})`
- Ensure ward.is_active = true

#### "Duplicate complaint detected"
- This is expected within 500m radius of same type in 7 days
- Check complaint_id in error response for existing complaint
- Can be overridden by admin if necessary

#### "Complaint limit exceeded"
- Citizens limited to 2 complaints/week
- Wait for old complaints to age out
- Check: `db.complaints.find({user_id: ObjectId("..."), created_at: {$gte: Date(...)}})`

#### MongoDB Connection Error
```bash
# Verify MongoDB is running
mongodb-compass mongodb://localhost:27017/civifix

# Check connection string in .env
# Verify network access if using Atlas
```

#### JWT Token Issues
```bash
# Decode token to check expiry
python -c "import jwt; print(jwt.decode('token', options={'verify_signature': False}))"

# Refresh token endpoint
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

#### Performance Issues
```bash
# Check indexes
db.complaints.getIndexes()

# Monitor query performance
db.setProfilingLevel(1)  # Enable profiling
db.system.profile.find().limit(10).sort({ts: -1}).pretty()

# Check MongoDB stats
mongosh
> db.stats()
> db.complaints.stats()
```

## 📝 Logging

Logs stored in `logs/` directory:
- `app.log`: General application logs
- `errors.log`: Error-only logs
- `access.log`: API access logs

View logs:
```bash
tail -f logs/app.log
grep "ERROR" logs/errors.log
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [JWT.io](https://jwt.io/)

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages and status codes
3. Check MongoDB connection and indexes
4. Verify environment variables
5. Contact development team

---

**Last Updated**: May 24, 2026
**Version**: 1.0.0
**Status**: Production Ready
