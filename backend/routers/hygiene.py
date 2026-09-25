import os
import uuid
import shutil
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import HygieneUpdate, Provider, User
from backend.schemas import HygieneOut
from backend.auth_utils import require_role

router = APIRouter(tags=["Hygiene Updates"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
HYGIENE_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "hygiene")
os.makedirs(HYGIENE_UPLOAD_DIR, exist_ok=True)


@router.get("/api/providers/{provider_id}/hygiene", response_model=List[HygieneOut])
def get_provider_hygiene_updates(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns all recent hygiene update photos submitted by the provider.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    updates = db.query(HygieneUpdate).filter(
        HygieneUpdate.provider_id == provider_id
    ).order_by(HygieneUpdate.date_posted.desc()).all()

    result = []
    for u in updates:
        result.append({
            "id": u.id,
            "provider_id": u.provider_id,
            "provider_name": provider.service_name,
            "image_path": u.image_path,
            "title": u.title,
            "description": u.description,
            "date_posted": u.date_posted,
            "disclaimer": u.disclaimer
        })
    return result


@router.get("/api/providers/{provider_id}/hygiene/today")
def get_today_hygiene_update(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns the most recent hygiene update posted today (or latest available).
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    latest = db.query(HygieneUpdate).filter(
        HygieneUpdate.provider_id == provider_id
    ).order_by(HygieneUpdate.date_posted.desc()).first()

    if not latest:
        return {"has_update": False, "message": "No hygiene updates posted yet."}

    return {
        "has_update": True,
        "id": latest.id,
        "provider_id": latest.provider_id,
        "provider_name": provider.service_name,
        "image_path": latest.image_path,
        "title": latest.title,
        "description": latest.description,
        "date_posted": latest.date_posted,
        "disclaimer": latest.disclaimer
    }


@router.post("/api/providers/hygiene", response_model=HygieneOut)
async def upload_hygiene_update(
    title: str = Form("Daily Kitchen & Food Prep Hygiene"),
    description: Optional[str] = Form(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Allows a provider to upload their daily kitchen cleanliness / prep photo.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    if not image_file or not image_file.filename:
        raise HTTPException(status_code=400, detail="Image file is required.")

    ext = os.path.splitext(image_file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are allowed.")

    filename = f"hygiene_{provider.id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(HYGIENE_UPLOAD_DIR, filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    relative_path = f"/uploads/hygiene/{filename}"

    new_update = HygieneUpdate(
        provider_id=provider.id,
        image_path=relative_path,
        title=title,
        description=description,
        disclaimer="Provider-submitted daily hygiene update (not laboratory certified)"
    )
    db.add(new_update)
    db.commit()
    db.refresh(new_update)

    return {
        "id": new_update.id,
        "provider_id": new_update.provider_id,
        "provider_name": provider.service_name,
        "image_path": new_update.image_path,
        "title": new_update.title,
        "description": new_update.description,
        "date_posted": new_update.date_posted,
        "disclaimer": new_update.disclaimer
    }


@router.delete("/api/hygiene/{update_id}")
def delete_hygiene_update(
    update_id: int,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Provider can delete an outdated hygiene record.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    update = db.query(HygieneUpdate).filter(
        HygieneUpdate.id == update_id,
        HygieneUpdate.provider_id == provider.id
    ).first()

    if not update:
        raise HTTPException(status_code=404, detail="Hygiene update not found or unauthorized.")

    db.delete(update)
    db.commit()
    return {"message": "Hygiene update removed successfully."}
