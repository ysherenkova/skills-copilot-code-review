"""
Announcement endpoints for the High School Management System API
"""

from datetime import date
import re
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _parse_date(value: Optional[str], field_name: str, required: bool = False) -> Optional[str]:
    if not value:
        if required:
            raise HTTPException(status_code=400, detail=f"{field_name} is required")
        return None

    try:
        parsed_date = date.fromisoformat(value)
        return parsed_date.isoformat()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be in YYYY-MM-DD format"
        ) from exc


def _validate_announcement_data(message: str, end_date: str, start_date: Optional[str] = None) -> Dict[str, Any]:
    clean_message = message.strip() if message else ""
    if not clean_message:
        raise HTTPException(status_code=400, detail="Message is required")
    if len(clean_message) > 500:
        raise HTTPException(status_code=400, detail="Message must be 500 characters or less")

    parsed_start_date = _parse_date(start_date, "start_date")
    parsed_end_date = _parse_date(end_date, "end_date", required=True)

    if parsed_start_date and parsed_start_date > parsed_end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

    return {
        "message": clean_message,
        "start_date": parsed_start_date,
        "end_date": parsed_end_date
    }


def _require_teacher(teacher_username: Optional[str]) -> Dict[str, Any]:
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _is_active_announcement(announcement: Dict[str, Any], today: date) -> bool:
    start_date = announcement.get("start_date")
    end_date = announcement.get("end_date")

    if not end_date:
        return False

    if start_date and start_date > today.isoformat():
        return False

    return end_date >= today.isoformat()


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get active announcements for public display"""
    today = date.today()
    announcements: List[Dict[str, Any]] = []

    for announcement in announcements_collection.find().sort("end_date", 1):
        if not _is_active_announcement(announcement, today):
            continue

        announcements.append({
            "id": announcement.get("_id"),
            "message": announcement.get("message", ""),
            "start_date": announcement.get("start_date"),
            "end_date": announcement.get("end_date")
        })

    return announcements


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements_for_management(teacher_username: str = Query(...)) -> List[Dict[str, Any]]:
    """Get all announcements for authenticated management"""
    _require_teacher(teacher_username)

    announcements: List[Dict[str, Any]] = []
    for announcement in announcements_collection.find().sort("end_date", 1):
        announcements.append({
            "id": announcement.get("_id"),
            "message": announcement.get("message", ""),
            "start_date": announcement.get("start_date"),
            "end_date": announcement.get("end_date")
        })

    return announcements


@router.post("", response_model=Dict[str, Any])
def create_announcement(
    message: str,
    end_date: str,
    start_date: Optional[str] = None,
    teacher_username: str = Query(...)
) -> Dict[str, Any]:
    """Create a new announcement (authenticated)"""
    _require_teacher(teacher_username)

    payload = _validate_announcement_data(
        message=message,
        start_date=start_date,
        end_date=end_date
    )

    announcement_id = re.sub(r"[^a-z0-9-]", "", payload["message"].lower().replace(" ", "-"))
    if not announcement_id:
        announcement_id = f"announcement-{date.today().isoformat()}"

    exists = announcements_collection.find_one({"_id": announcement_id})
    if exists:
        raise HTTPException(status_code=400, detail="Announcement ID conflict, please adjust the message")

    announcements_collection.insert_one({
        "_id": announcement_id,
        **payload
    })

    return {
        "message": "Announcement created successfully",
        "announcement": {
            "id": announcement_id,
            **payload
        }
    }


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    message: str,
    end_date: str,
    start_date: Optional[str] = None,
    teacher_username: str = Query(...)
) -> Dict[str, Any]:
    """Update an existing announcement (authenticated)"""
    _require_teacher(teacher_username)

    payload = _validate_announcement_data(
        message=message,
        start_date=start_date,
        end_date=end_date
    )

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": payload}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {
        "message": "Announcement updated successfully",
        "announcement": {
            "id": announcement_id,
            **payload
        }
    }


@router.delete("/{announcement_id}", response_model=Dict[str, Any])
def delete_announcement(announcement_id: str, teacher_username: str = Query(...)) -> Dict[str, Any]:
    """Delete an announcement (authenticated)"""
    _require_teacher(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
