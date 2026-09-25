from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Provider, AvailabilityLog, CustomerSubscription, Notification, User, Conversation
from backend.schemas import AvailabilityUpdate, AvailabilityOut
from backend.auth_utils import require_role

router = APIRouter(tags=["Availability & Leave"])


@router.get("/api/providers/{provider_id}/availability")
def get_provider_availability(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns current availability status and scheduled leave notice for a provider.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    return {
        "provider_id": provider.id,
        "service_name": provider.service_name,
        "is_available": provider.is_available,
        "leave_notice": provider.leave_notice,
        "leave_start": provider.leave_start,
        "leave_end": provider.leave_end,
        "status_text": "Available" if provider.is_available else "Currently Unavailable"
    }


@router.post("/api/providers/availability")
def update_provider_availability(
    payload: AvailabilityUpdate,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Provider toggles availability or schedules advance leave pre-notice.
    Broadcasts notifications to all subscribed/connected students automatically.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    # Update provider fields
    provider.is_available = payload.is_available
    provider.leave_start = payload.start_date
    provider.leave_end = payload.end_date
    provider.leave_notice = payload.reason_message

    # Log the availability change
    log_entry = AvailabilityLog(
        provider_id=provider.id,
        is_available=payload.is_available,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason_message=payload.reason_message
    )
    db.add(log_entry)

    # Find all students who subscribe or have conversations with this provider
    subscribed_student_user_ids = set()

    # From subscriptions
    subs = db.query(CustomerSubscription).filter(
        CustomerSubscription.provider_id == provider.id,
        CustomerSubscription.status == "active"
    ).all()
    for s in subs:
        if s.student and s.student.user_id:
            subscribed_student_user_ids.add(s.student.user_id)

    # From conversations
    convs = db.query(Conversation).filter(Conversation.provider_id == provider.id).all()
    for c in convs:
        if c.student and c.student.user_id:
            subscribed_student_user_ids.add(c.student.user_id)

    # Compose alert message
    if not payload.is_available:
        if payload.start_date and payload.end_date:
            alert_msg = f"{provider.service_name} will be unavailable from {payload.start_date.strftime('%d %b')} to {payload.end_date.strftime('%d %b')}. Reason: {payload.reason_message or 'Personal Leave'}."
        else:
            alert_msg = f"{provider.service_name} is currently unavailable. Notice: {payload.reason_message or 'Temporarily closed'}."
        alert_title = f"⚠️ Alert: {provider.service_name} Leave Notice"
    else:
        alert_msg = f"{provider.service_name} is now available and accepting meal requests!"
        alert_title = f"✅ {provider.service_name} is Available"

    for student_user_id in subscribed_student_user_ids:
        notification = Notification(
            user_id=student_user_id,
            title=alert_title,
            message=alert_msg,
            notification_type="availability_alert",
            link_url=f"/provider-profile.html?id={provider.id}"
        )
        db.add(notification)

    db.commit()
    db.refresh(provider)

    return {
        "message": "Availability and leave pre-notice updated successfully.",
        "provider_id": provider.id,
        "is_available": provider.is_available,
        "leave_notice": provider.leave_notice,
        "leave_start": provider.leave_start,
        "leave_end": provider.leave_end,
        "students_notified": len(subscribed_student_user_ids)
    }
