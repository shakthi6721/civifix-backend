"""Complaint model for MongoDB"""
from datetime import datetime
from typing import Optional, List

def complaint_document(
    citizen_id: str,
    title: str,
    description: str,
    district: str,
    category: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    attachment_urls: Optional[List[str]] = None
) -> dict:
    """Create a complaint document"""
    return {
        "citizen_id": citizen_id,
        "title": title,
        "description": description,
        "district": district,
        "category": category,
        "latitude": latitude,
        "longitude": longitude,
        "attachment_urls": attachment_urls or [],
        "status": "PENDING",
        "inspector_id": None,
        "worker_id": None,
        "priority": "NORMAL",
        "assigned_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "resolved_at": None
    }


def complaint_history_document(
    complaint_id: str,
    old_status: str,
    new_status: str,
    changed_by: str,
    changed_by_role: str,
    notes: Optional[str] = None
) -> dict:
    """Create a complaint history document for audit trail"""
    return {
        "complaint_id": complaint_id,
        "old_status": old_status,
        "new_status": new_status,
        "changed_by": changed_by,
        "changed_by_role": changed_by_role,
        "notes": notes,
        "created_at": datetime.utcnow()
    }
