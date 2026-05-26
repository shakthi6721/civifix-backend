# Civifix Complaint Module - Quick Reference

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m uvicorn app.main:app --reload

# Run tests
pytest app/tests/test_complaints.py -v

# Access API docs
# Browser: http://localhost:8000/api/docs
```

## 📍 API Endpoints

### Wards
```
POST   /api/v1/wards
GET    /api/v1/wards/{ward_id}
PUT    /api/v1/wards/{ward_id}
GET    /api/v1/wards/district/{district_id}
GET    /api/v1/wards/inspector/{inspector_id}
GET    /api/v1/wards/search/{district_id}
PUT    /api/v1/wards/{ward_id}/deactivate
```

### Complaints
```
POST   /api/v1/complaints
GET    /api/v1/complaints/{complaint_id}
GET    /api/v1/complaints/my/dashboard
PUT    /api/v1/complaints/{id}/assign-worker
PUT    /api/v1/complaints/{id}/submit-work
PUT    /api/v1/complaints/{id}/approve
PUT    /api/v1/complaints/{id}/reject
GET    /api/v1/complaints/ward/{ward_id}
GET    /api/v1/complaints/inspector/dashboard
```

## 🔑 Key Classes

### Services
- **ComplaintService** - Complaint lifecycle (10 methods)
- **WardService** - Ward management (8 methods)
- **NotificationService** - Notifications (5 methods)
- **FileUploadService** - File uploads (S3/MinIO)

### Repositories
- **ComplaintRepository** - Complaint data access (25+ methods)
- **WardRepository** - Ward CRUD (15+ methods)
- **NotificationRepository** - Notification tracking (8 methods)

### Validators
- **ComplaintValidator** - Input validation
- **DuplicateComplaintDetector** - Duplicate detection
- **SpamDetector** - Spam prevention

## 📋 Complaint Status Flow

```
OPEN → WORKING → APPROVAL → CLOSED
                    ↓
                WORKING (if rejected)
```

## 🔐 RBAC Permissions

| Role | Create | Assign | Approve | View |
|------|--------|--------|---------|------|
| CITIZEN | Own | ❌ | ❌ | Own |
| INSPECTOR | ❌ | ✅ | ✅ | Assigned |
| WORKER | ❌ | ❌ | ❌ | Assigned |
| DISTRICT_ADMIN | ❌ | ❌ | ❌ | District |
| SUPER_ADMIN | ✅ | ✅ | ✅ | All |

## 🛡️ Validation Rules

### Spam Prevention
- Max 2 complaints/week per citizen
- Max 1 complaint/day per citizen
- No repetitive descriptions

### Duplicate Detection
- Same complaint type
- Within 500 meters radius
- Within 7-day window

### Input Validation
- GPS: -90 to 90 (lat), -180 to 180 (lon)
- Description: 10-1000 chars
- Images: JPG, PNG, GIF, WEBP, BMP (max 5)
- Email: Valid email format
- Phone: 10-digit Indian number (6-9 start)

## 📊 Complaint Status Codes

| Status | Meaning |
|--------|---------|
| OPEN | Citizen reported, awaiting inspector action |
| WORKING | Worker assigned, task in progress |
| APPROVAL | Worker submitted, inspector reviewing |
| CLOSED | Inspector approved, complaint resolved |

## 🗄️ Database Collections

```
complaints
  ├─ _id: ObjectId
  ├─ complaint_id: String (unique)
  ├─ user_id: ObjectId
  ├─ ward_id: ObjectId
  ├─ status: String
  ├─ created_at: DateTime
  └─ ...

complaint_history
  ├─ complaint_id: ObjectId
  ├─ action: String
  ├─ performed_by: ObjectId
  └─ timestamp: DateTime

wards
  ├─ _id: ObjectId
  ├─ district_id: ObjectId
  ├─ ward_number: String (unique per district)
  ├─ inspector_id: ObjectId
  └─ ...

notifications
  ├─ user_id: ObjectId
  ├─ complaint_id: ObjectId
  ├─ status: String
  └─ ...
```

## 🔧 Common Operations

### Create Complaint
```bash
curl -X POST http://localhost:8000/api/v1/complaints \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ward_id": "...",
    "complaint_type": "GARBAGE",
    "description": "...",
    "latitude": 13.0827,
    "longitude": 80.2707
  }'
```

### Assign Worker
```bash
curl -X PUT http://localhost:8000/api/v1/complaints/<id>/assign-worker \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "...",
    "deadline": "2026-06-15T00:00:00"
  }'
```

### Approve Complaint
```bash
curl -X PUT http://localhost:8000/api/v1/complaints/<id>/approve \
  -H "Authorization: Bearer <token>" \
  -d '{
    "note": "Work completed successfully"
  }'
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Ward not found | Check ward_id, verify ward exists |
| Duplicate complaint | Within 500m, same type, last 7 days |
| Limit exceeded | Max 2/week, 1/day per citizen |
| Auth error | Check token expiry, refresh if needed |
| DB connection | Verify MONGODB_URL in .env |

## 📁 Important Files

```
app/
├── services/
│   ├── complaint_service.py    # Core logic
│   ├── ward_service.py         # Ward logic
│   └── notification_service.py # Notifications
├── repositories/
│   ├── complaint_repository.py # Data access
│   └── ward_repository.py      # Ward data
├── api/v1/
│   ├── complaints_routes.py    # API endpoints
│   └── wards_routes.py         # Ward endpoints
├── schemas/
│   └── complaint_schema.py     # Validation
└── utils/
    └── complaint_validators.py # Validators
```

## 📝 Environment Variables

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=civifix
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
LOG_LEVEL=INFO
```

## ✅ All Features Implemented

- [x] Complaint creation with validation
- [x] Ward management
- [x] Worker assignment
- [x] Approval workflow
- [x] Duplicate detection
- [x] Spam prevention
- [x] Notifications
- [x] Audit logging
- [x] File uploads (S3/MinIO)
- [x] Pagination & filtering
- [x] RBAC authorization
- [x] Error handling
- [x] Comprehensive tests
- [x] API documentation
- [x] Docker setup

---

**Last Updated**: May 24, 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
