from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ---------------- Auth & User Schemas ----------------
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    role: str = Field(..., description="'student' or 'provider'")
    # Additional student fields (if registering as student)
    college_name: Optional[str] = "Pune University / College"
    hostel_area: Optional[str] = "Dhankawadi"
    meal_preference: Optional[str] = "veg"
    # Additional provider fields (if registering as provider)
    service_name: Optional[str] = None
    area: Optional[str] = "Dhankawadi, Pune"
    food_type: Optional[str] = "Pure Veg"
    single_meal_price: Optional[float] = 80.0
    monthly_price: Optional[float] = 2400.0



class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username_or_email: str
    password: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    username: str
    full_name: str
    profile_id: int  # student_id or provider_id


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Provider Schemas ----------------
class ProviderOut(BaseModel):
    id: int
    user_id: int
    service_name: str
    owner_name: str
    description: Optional[str]
    area: str
    full_address: Optional[str]
    contact_number: str
    food_type: str
    single_meal_price: float
    monthly_price: float
    delivery_available: bool
    profile_image: Optional[str]
    is_available: bool
    leave_notice: Optional[str]
    leave_start: Optional[date]
    leave_end: Optional[date]
    average_rating: float = 0.0
    rating_count: int = 0
    active_customer_count: int = 0
    today_hygiene_image: Optional[str] = None

    class Config:
        from_attributes = True


class ProviderUpdate(BaseModel):
    service_name: Optional[str] = None
    owner_name: Optional[str] = None
    description: Optional[str] = None
    area: Optional[str] = None
    full_address: Optional[str] = None
    contact_number: Optional[str] = None
    food_type: Optional[str] = None
    single_meal_price: Optional[float] = None
    monthly_price: Optional[float] = None
    delivery_available: Optional[bool] = None


# ---------------- Menu Item Schemas ----------------
class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    meal_type: str = "Lunch"  # Lunch, Dinner, Breakfast, All Day
    category: str = "Veg"    # Veg, Non-Veg, Special, Jain
    price: float = Field(..., gt=0)
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    meal_type: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


class MenuItemOut(BaseModel):
    id: int
    provider_id: int
    name: str
    description: Optional[str]
    meal_type: str
    category: str
    price: float
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Rating & Review Schemas ----------------
class RatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(..., min_length=5, max_length=1000)
    food_quality_score: Optional[int] = Field(5, ge=1, le=5)
    hygiene_score: Optional[int] = Field(5, ge=1, le=5)


class RatingOut(BaseModel):
    id: int
    provider_id: int
    student_id: int
    student_name: str
    student_college: Optional[str]
    rating: int
    review_text: str
    proof_image: Optional[str]
    food_quality_score: Optional[int]
    hygiene_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Hygiene Update Schemas ----------------
class HygieneOut(BaseModel):
    id: int
    provider_id: int
    provider_name: str
    image_path: str
    title: str
    description: Optional[str]
    date_posted: datetime
    disclaimer: str

    class Config:
        from_attributes = True


# ---------------- Availability & Leave Schemas ----------------
class AvailabilityUpdate(BaseModel):
    is_available: bool
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason_message: Optional[str] = None


class AvailabilityOut(BaseModel):
    id: int
    provider_id: int
    is_available: bool
    start_date: Optional[date]
    end_date: Optional[date]
    reason_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Advertisement Schemas ----------------
class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=5)
    banner_type: str = "offer"  # offer, announcement, discount
    valid_until: Optional[date] = None


class AdvertisementOut(BaseModel):
    id: int
    provider_id: int
    provider_name: str
    title: str
    description: str
    image_url: Optional[str]
    banner_type: str
    is_active: bool
    valid_until: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Customer / Subscription Schemas ----------------
class SubscriptionCreate(BaseModel):
    provider_id: int
    plan_type: str = "Monthly Lunch & Dinner"
    notes: Optional[str] = None


class CustomerSubscriptionOut(BaseModel):
    id: int
    provider_id: int
    student_id: int
    student_name: str
    student_phone: Optional[str]
    student_area: Optional[str]
    plan_type: str
    status: str
    start_date: date
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Chat & Message Schemas ----------------
class ConversationOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    provider_id: int
    provider_name: str
    last_message: Optional[str]
    unread_count: int = 0
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    message_text: str = Field(..., min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: str
    sender_role: str
    message_text: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- Notification Schemas ----------------
class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    link_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
