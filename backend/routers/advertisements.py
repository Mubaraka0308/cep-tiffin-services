import os
import uuid
import shutil
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Advertisement, Provider, User
from backend.schemas import AdvertisementOut
from backend.auth_utils import require_role

router = APIRouter(tags=["Advertisements"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
AD_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "advertisements")
os.makedirs(AD_UPLOAD_DIR, exist_ok=True)


@router.get("/api/advertisements", response_model=List[AdvertisementOut])
def get_active_advertisements(db: Session = Depends(get_db)):
    """
    Returns all active provider advertisements for the student dashboard & home page.
    """
    ads = db.query(Advertisement).filter(Advertisement.is_active == True).order_by(
        Advertisement.created_at.desc()
    ).all()

    result = []
    for a in ads:
        provider = a.provider
        result.append({
            "id": a.id,
            "provider_id": a.provider_id,
            "provider_name": provider.service_name if provider else "Tiffin Partner",
            "title": a.title,
            "description": a.description,
            "image_url": a.image_url,
            "banner_type": a.banner_type,
            "is_active": a.is_active,
            "valid_until": a.valid_until,
            "created_at": a.created_at
        })
    return result


@router.get("/api/providers/{provider_id}/advertisements", response_model=List[AdvertisementOut])
def get_provider_advertisements(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns advertisements created by a specific provider.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    ads = db.query(Advertisement).filter(
        Advertisement.provider_id == provider_id
    ).order_by(Advertisement.created_at.desc()).all()

    result = []
    for a in ads:
        result.append({
            "id": a.id,
            "provider_id": a.provider_id,
            "provider_name": provider.service_name,
            "title": a.title,
            "description": a.description,
            "image_url": a.image_url,
            "banner_type": a.banner_type,
            "is_active": a.is_active,
            "valid_until": a.valid_until,
            "created_at": a.created_at
        })
    return result


@router.post("/api/providers/advertisements", response_model=AdvertisementOut)
async def create_advertisement(
    title: str = Form(...),
    description: str = Form(...),
    banner_type: str = Form("offer"),
    valid_until: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Allows a provider to publish a special promotional banner/announcement.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    image_relative_path = None
    if image_file and image_file.filename:
        ext = os.path.splitext(image_file.filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            filename = f"ad_{provider.id}_{uuid.uuid4().hex[:8]}{ext}"
            dest = os.path.join(AD_UPLOAD_DIR, filename)
            with open(dest, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            image_relative_path = f"/uploads/advertisements/{filename}"

    parsed_date = None
    if valid_until:
        try:
            parsed_date = datetime.strptime(valid_until, "%Y-%m-%d").date()
        except Exception:
            pass

    new_ad = Advertisement(
        provider_id=provider.id,
        title=title.strip(),
        description=description.strip(),
        image_url=image_relative_path,
        banner_type=banner_type,
        is_active=True,
        valid_until=parsed_date
    )
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)

    return {
        "id": new_ad.id,
        "provider_id": new_ad.provider_id,
        "provider_name": provider.service_name,
        "title": new_ad.title,
        "description": new_ad.description,
        "image_url": new_ad.image_url,
        "banner_type": new_ad.banner_type,
        "is_active": new_ad.is_active,
        "valid_until": new_ad.valid_until,
        "created_at": new_ad.created_at
    }


@router.put("/api/advertisements/{ad_id}/toggle")
def toggle_advertisement_status(
    ad_id: int,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Toggle advertisement active/inactive state.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    ad = db.query(Advertisement).filter(
        Advertisement.id == ad_id,
        Advertisement.provider_id == provider.id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found or unauthorized.")

    ad.is_active = not ad.is_active
    db.commit()
    return {"message": "Status updated", "id": ad.id, "is_active": ad.is_active}


@router.delete("/api/advertisements/{ad_id}")
def delete_advertisement(
    ad_id: int,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Delete an advertisement.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    ad = db.query(Advertisement).filter(
        Advertisement.id == ad_id,
        Advertisement.provider_id == provider.id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found or unauthorized.")

    db.delete(ad)
    db.commit()
    return {"message": "Advertisement deleted successfully."}
