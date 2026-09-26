from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database import get_db
from backend.models import Conversation, Message, User, Student, Provider, Notification
from backend.schemas import ConversationOut, MessageCreate, MessageOut
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["Direct Chat"])


def _as_utc(dt: datetime) -> datetime:
    """Ensure naive UTC datetimes from DB serialize as aware UTC with 'Z' suffix."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("", response_model=List[ConversationOut])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all active chat conversations for the logged in user (student or provider).
    """
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            return []
        conversations = db.query(Conversation).filter(
            Conversation.student_id == student.id
        ).order_by(Conversation.last_message_at.desc()).all()

    elif current_user.role == "provider":
        provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
        if not provider:
            return []
        conversations = db.query(Conversation).filter(
            Conversation.provider_id == provider.id
        ).order_by(Conversation.last_message_at.desc()).all()

    else:
        return []

    result = []
    for conv in conversations:
        # Get last message
        last_msg = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()

        # Unread count
        unread = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        ).count()

        student_user = conv.student.user if conv.student else None
        provider_name = conv.provider.service_name if conv.provider else "Tiffin Service"
        updated_dt = conv.last_message_at or conv.created_at

        result.append({
            "id": conv.id,
            "student_id": conv.student_id,
            "student_name": student_user.full_name if student_user else "Student",
            "provider_id": conv.provider_id,
            "provider_name": provider_name,
            "last_message": last_msg.message_text if last_msg else "No messages yet",
            "unread_count": unread,
            "updated_at": _as_utc(updated_dt)
        })

    return result


@router.post("")
def start_or_get_conversation(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Starts a new conversation with a provider or opens the existing one.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Only students can initiate a conversation with providers.")

    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    conv = db.query(Conversation).filter(
        Conversation.student_id == student.id,
        Conversation.provider_id == provider.id
    ).first()

    if not conv:
        conv = Conversation(
            student_id=student.id,
            provider_id=provider.id,
            last_message_at=datetime.utcnow()
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return {
        "id": conv.id,
        "student_id": conv.student_id,
        "provider_id": conv.provider_id,
        "provider_name": provider.service_name,
        "created_at": _as_utc(conv.created_at)
    }


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves message history and marks received messages as read.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Authorization check
    is_authorized = False
    if current_user.role == "student" and conv.student and conv.student.user_id == current_user.id:
        is_authorized = True
    elif current_user.role == "provider" and conv.provider and conv.provider.user_id == current_user.id:
        is_authorized = True

    if not is_authorized:
        raise HTTPException(status_code=403, detail="Unauthorized to view this conversation.")

    # Mark incoming unread messages as read
    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    result = []
    for m in messages:
        sender = m.sender
        result.append({
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_id": m.sender_id,
            "sender_name": sender.full_name if sender else "User",
            "sender_role": sender.role if sender else "unknown",
            "message_text": m.message_text,
            "is_read": m.is_read,
            "created_at": _as_utc(m.created_at)
        })

    return result


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sends a direct message in a conversation and triggers an in-app notification for the recipient.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Authorization & recipient determination
    recipient_user_id = None
    if current_user.role == "student":
        if not conv.student or conv.student.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized.")
        recipient_user_id = conv.provider.user_id if conv.provider else None
    elif current_user.role == "provider":
        if not conv.provider or conv.provider.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized.")
        recipient_user_id = conv.student.user_id if conv.student else None
    else:
        raise HTTPException(status_code=403, detail="Invalid user role.")

    now = datetime.utcnow()
    new_message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        message_text=payload.message_text.strip(),
        is_read=False,
        created_at=now
    )
    db.add(new_message)

    # Update last_message_at on conversation
    conv.last_message_at = now

    # Create notification for recipient
    if recipient_user_id:
        notif = Notification(
            user_id=recipient_user_id,
            title=f"New message from {current_user.full_name}",
            message=payload.message_text[:80] + ("..." if len(payload.message_text) > 80 else ""),
            notification_type="chat_message",
            link_url=f"/chat.html?conv={conv.id}"
        )
        db.add(notif)

    db.commit()
    db.refresh(new_message)

    return {
        "id": new_message.id,
        "conversation_id": new_message.conversation_id,
        "sender_id": new_message.sender_id,
        "sender_name": current_user.full_name,
        "sender_role": current_user.role,
        "message_text": new_message.message_text,
        "is_read": new_message.is_read,
        "created_at": _as_utc(new_message.created_at)
    }
