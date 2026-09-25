import os
import uuid
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Rating, Provider, Student, User, Notification
from backend.schemas import RatingOut
from backend.auth_utils import require_role

router = APIRouter(prefix="/api/providers/{provider_id}/ratings", tags=["Ratings & Reviews"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
RATING_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "ratings")
os.makedirs(RATING_UPLOAD_DIR, exist_ok=True)


@router.get("")
def get_provider_ratings(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns ratings and reviews for a provider, including overall and weekly statistics.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    ratings = db.query(Rating).filter(
        Rating.provider_id == provider_id
    ).order_by(Rating.created_at.desc()).all()

    # Calculate overall stats
    total_count = len(ratings)
    avg_rating = round(sum(r.rating for r in ratings) / total_count, 1) if total_count > 0 else 0.0

    # Calculate weekly ratings (ratings submitted within the past 7 days)
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_ratings = [r for r in ratings if r.created_at >= one_week_ago]
    weekly_count = len(weekly_ratings)
    weekly_avg = round(sum(r.rating for r in weekly_ratings) / weekly_count, 1) if weekly_count > 0 else avg_rating

    reviews_list = []
    for r in ratings:
        student = r.student
        user = student.user if student else None
        reviews_list.append({
            "id": r.id,
            "provider_id": r.provider_id,
            "student_id": r.student_id,
            "student_name": user.full_name if user else "Verified Student",
            "student_college": student.college_name if student else "Pune College",
            "rating": r.rating,
            "review_text": r.review_text,
            "proof_image": r.proof_image,
            "food_quality_score": r.food_quality_score,
            "hygiene_score": r.hygiene_score,
            "created_at": r.created_at
        })

    return {
        "provider_id": provider_id,
        "provider_name": provider.service_name,
        "average_rating": avg_rating,
        "total_reviews": total_count,
        "weekly_average_rating": weekly_avg,
        "weekly_reviews_count": weekly_count,
        "reviews": reviews_list
    }


@router.post("")
async def create_rating(
    provider_id: int,
    rating: int = Form(...),
    review_text: str = Form(...),
    food_quality_score: Optional[int] = Form(5),
    hygiene_score: Optional[int] = Form(5),
    proof_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    """
    Submits a genuine student rating and review with optional meal photo proof.
    Includes spam-prevention: limits reviews to 1 per student per provider per 24 hours.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    # Validation
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 stars.")

    if len(review_text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please write a genuine review (at least 5 characters).")

    # Anti-spam restriction: check if student reviewed this provider in the last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_review = db.query(Rating).filter(
        Rating.provider_id == provider_id,
        Rating.student_id == student.id,
        Rating.created_at >= twenty_four_hours_ago
    ).first()

    if recent_review:
        raise HTTPException(
            status_code=400,
            detail="You have already submitted a review for this provider today. You can post another review after 24 hours."
        )

    # Handle optional proof image upload
    image_relative_path = None
    if proof_image and proof_image.filename:
        ext = os.path.splitext(proof_image.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are allowed.")

        filename = f"proof_{uuid.uuid4().hex[:10]}{ext}"
        destination = os.path.join(RATING_UPLOAD_DIR, filename)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(proof_image.file, buffer)
        image_relative_path = f"/uploads/ratings/{filename}"

    new_rating = Rating(
        provider_id=provider.id,
        student_id=student.id,
        rating=rating,
        review_text=review_text.strip(),
        proof_image=image_relative_path,
        food_quality_score=food_quality_score or 5,
        hygiene_score=hygiene_score or 5
    )
    db.add(new_rating)

    # Notify provider about the new review
    notification = Notification(
        user_id=provider.user_id,
        title=f"New {rating}-Star Review Received! ⭐",
        message=f"{current_user.full_name} left a review: \"{review_text[:60]}...\"",
        notification_type="new_rating"
    )
    db.add(notification)
    db.commit()
    db.refresh(new_rating)

    return {
        "message": "Review submitted successfully! Thank you for helping other students.",
        "id": new_rating.id,
        "rating": new_rating.rating,
        "review_text": new_rating.review_text,
        "proof_image": new_rating.proof_image
    }
