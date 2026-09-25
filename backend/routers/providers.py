from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import (
    Provider, User, Student, Rating, MenuItem,
    HygieneUpdate, CustomerSubscription, Notification
)
from backend.schemas import ProviderOut, ProviderUpdate, CustomerSubscriptionOut, SubscriptionCreate
from backend.auth_utils import get_current_user, require_role

router = APIRouter(prefix="/api/providers", tags=["Providers"])


def enrich_provider_data(provider: Provider, db: Session) -> dict:
    """
    Helper function to calculate average rating, rating count,
    customer count, and get the latest hygiene photo for a provider.
    """
    # Average rating and total count
    rating_stats = db.query(
        func.coalesce(func.avg(Rating.rating), 0.0),
        func.count(Rating.id)
    ).filter(Rating.provider_id == provider.id).first()

    avg_rating = round(float(rating_stats[0]), 1) if rating_stats else 0.0
    rating_cnt = int(rating_stats[1]) if rating_stats else 0

    # Active customer count
    cust_count = db.query(CustomerSubscription).filter(
        CustomerSubscription.provider_id == provider.id,
        CustomerSubscription.status == "active"
    ).count()

    # Latest hygiene photo
    latest_hygiene = db.query(HygieneUpdate).filter(
        HygieneUpdate.provider_id == provider.id
    ).order_by(HygieneUpdate.date_posted.desc()).first()

    return {
        "id": provider.id,
        "user_id": provider.user_id,
        "service_name": provider.service_name,
        "owner_name": provider.owner_name,
        "description": provider.description,
        "area": provider.area,
        "full_address": provider.full_address,
        "contact_number": provider.contact_number,
        "food_type": provider.food_type,
        "single_meal_price": provider.single_meal_price,
        "monthly_price": provider.monthly_price,
        "delivery_available": provider.delivery_available,
        "profile_image": provider.profile_image,
        "is_available": provider.is_available,
        "leave_notice": provider.leave_notice,
        "leave_start": provider.leave_start,
        "leave_end": provider.leave_end,
        "average_rating": avg_rating,
        "rating_count": rating_cnt,
        "active_customer_count": cust_count,
        "today_hygiene_image": latest_hygiene.image_path if latest_hygiene else None
    }


@router.get("", response_model=List[ProviderOut])
def get_providers(
    search: Optional[str] = Query(None, description="Search by name, area, or food description"),
    area: Optional[str] = Query(None, description="Filter by area (e.g., Dhankawadi, Katraj)"),
    food_type: Optional[str] = Query(None, description="Filter by food type (Pure Veg, Veg & Non-Veg)"),
    max_price: Optional[float] = Query(None, description="Max single meal price"),
    available_only: Optional[bool] = Query(False, description="Filter only currently available providers"),
    db: Session = Depends(get_db)
):
    """
    Search and browse tiffin providers with filtering options.
    """
    query = db.query(Provider)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Provider.service_name.ilike(search_pattern)) |
            (Provider.area.ilike(search_pattern)) |
            (Provider.description.ilike(search_pattern)) |
            (Provider.food_type.ilike(search_pattern))
        )

    if area and area.strip() and area.lower() != "all":
        query = query.filter(Provider.area.ilike(f"%{area.strip()}%"))

    if food_type and food_type.strip() and food_type.lower() != "all":
        query = query.filter(Provider.food_type.ilike(f"%{food_type.strip()}%"))

    if max_price:
        query = query.filter(Provider.single_meal_price <= max_price)

    if available_only:
        query = query.filter(Provider.is_available == True)

    providers = query.all()
    results = [enrich_provider_data(p, db) for p in providers]
    return results


@router.get("/current/me", response_model=ProviderOut)
def get_my_provider_profile(
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Get profile data for the currently logged in provider.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")
    return enrich_provider_data(provider, db)


@router.put("/current/me", response_model=ProviderOut)
def update_my_provider_profile(
    payload: ProviderUpdate,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Update profile details for the logged in provider.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    for field, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(provider, field, val)

    db.commit()
    db.refresh(provider)
    return enrich_provider_data(provider, db)


@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Get key performance and operational stats for the provider dashboard.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    enriched = enrich_provider_data(provider, db)
    menu_count = db.query(MenuItem).filter(MenuItem.provider_id == provider.id).count()
    hygiene_count = db.query(HygieneUpdate).filter(HygieneUpdate.provider_id == provider.id).count()

    return {
        "provider_id": provider.id,
        "service_name": provider.service_name,
        "is_available": provider.is_available,
        "leave_notice": provider.leave_notice,
        "leave_start": provider.leave_start,
        "leave_end": provider.leave_end,
        "active_customers": enriched["active_customer_count"],
        "average_rating": enriched["average_rating"],
        "total_reviews": enriched["rating_count"],
        "total_menu_items": menu_count,
        "total_hygiene_updates": hygiene_count,
        "today_hygiene_image": enriched["today_hygiene_image"]
    }


@router.get("/dashboard/customers", response_model=List[CustomerSubscriptionOut])
def get_provider_customers(
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    View current subscribed students/customers without exposing unnecessary sensitive info.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    subscriptions = db.query(CustomerSubscription).filter(
        CustomerSubscription.provider_id == provider.id
    ).order_by(CustomerSubscription.created_at.desc()).all()

    result = []
    for sub in subscriptions:
        student = sub.student
        user = student.user if student else None
        result.append({
            "id": sub.id,
            "provider_id": sub.provider_id,
            "student_id": sub.student_id,
            "student_name": user.full_name if user else "Student Customer",
            "student_phone": user.phone if user else None,
            "student_area": student.hostel_area if student else None,
            "plan_type": sub.plan_type,
            "status": sub.status,
            "start_date": sub.start_date,
            "notes": sub.notes,
            "created_at": sub.created_at
        })
    return result


@router.post("/{provider_id}/subscribe", response_model=CustomerSubscriptionOut)
def subscribe_to_provider(
    provider_id: int,
    payload: SubscriptionCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    """
    A student requests/joins a tiffin subscription plan for a provider.
    Increases provider's active customer count and notifies the provider.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    # Check for existing active subscription
    existing_sub = db.query(CustomerSubscription).filter(
        CustomerSubscription.provider_id == provider_id,
        CustomerSubscription.student_id == student.id,
        CustomerSubscription.status == "active"
    ).first()

    if existing_sub:
        return {
            "id": existing_sub.id,
            "provider_id": existing_sub.provider_id,
            "student_id": existing_sub.student_id,
            "student_name": current_user.full_name,
            "student_phone": current_user.phone,
            "student_area": student.hostel_area,
            "plan_type": existing_sub.plan_type,
            "status": existing_sub.status,
            "start_date": existing_sub.start_date,
            "notes": existing_sub.notes,
            "created_at": existing_sub.created_at
        }

    new_sub = CustomerSubscription(
        provider_id=provider.id,
        student_id=student.id,
        plan_type=payload.plan_type,
        status="active",
        notes=payload.notes
    )
    db.add(new_sub)

    # Notify provider
    notify = Notification(
        user_id=provider.user_id,
        title="New Customer Subscribed! 🍲",
        message=f"{current_user.full_name} from {student.hostel_area} subscribed to your {payload.plan_type} plan.",
        notification_type="new_customer"
    )
    db.add(notify)
    db.commit()
    db.refresh(new_sub)

    return {
        "id": new_sub.id,
        "provider_id": new_sub.provider_id,
        "student_id": new_sub.student_id,
        "student_name": current_user.full_name,
        "student_phone": current_user.phone,
        "student_area": student.hostel_area,
        "plan_type": new_sub.plan_type,
        "status": new_sub.status,
        "start_date": new_sub.start_date,
        "notes": new_sub.notes,
        "created_at": new_sub.created_at
    }


@router.get("/{provider_id}", response_model=ProviderOut)
def get_provider_by_id(provider_id: int, db: Session = Depends(get_db)):
    """
    Get full details for a specific provider.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")
    return enrich_provider_data(provider, db)
