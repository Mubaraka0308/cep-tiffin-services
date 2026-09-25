from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Student, Provider, PasswordResetToken
from backend.schemas import UserRegister, UserLogin, TokenResponse, UserOut, ForgotPasswordRequest, ResetPasswordRequest
from backend.auth_utils import (
    hash_password, verify_password, create_access_token,
    get_current_user, create_password_reset_token, send_reset_email
)
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new student or tiffin provider and creates their specific profile.
    """
    # Check if email or username already exists
    existing_user = db.query(User).filter(
        (User.email == payload.email) | (User.username == payload.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )

    role = payload.role.lower().strip()
    if role not in ["student", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'student' or 'provider'."
        )

    # Create User record
    new_user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    profile_id = 0
    # Create role-specific profile
    if role == "student":
        student_profile = Student(
            user_id=new_user.id,
            college_name=payload.college_name or "Pune University / College",
            hostel_area=payload.hostel_area or "Dhankawadi",
            meal_preference=payload.meal_preference or "veg"
        )
        db.add(student_profile)
        db.commit()
        db.refresh(student_profile)
        profile_id = student_profile.id

    elif role == "provider":
        service_name = payload.service_name or f"{payload.full_name}'s Tiffins"
        provider_profile = Provider(
            user_id=new_user.id,
            service_name=service_name,
            owner_name=payload.full_name,
            area=payload.area or "Dhankawadi, Pune",
            contact_number=payload.phone or "9876543210",
            food_type=payload.food_type or "Pure Veg",
            single_meal_price=payload.single_meal_price or 80.0,
            monthly_price=payload.monthly_price or 2400.0,
            description=f"Fresh, home-cooked daily meals prepared with love and hygiene by {payload.full_name}."
        )
        db.add(provider_profile)
        db.commit()
        db.refresh(provider_profile)
        profile_id = provider_profile.id

    # Create JWT Access Token
    token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": new_user.id,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "profile_id": profile_id
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user with email/username and password.
    """
    user = db.query(User).filter(
        (User.email == payload.username_or_email) | (User.username == payload.username_or_email)
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password."
        )

    profile_id = 0
    if user.role == "student" and user.student_profile:
        profile_id = user.student_profile.id
    elif user.role == "provider" and user.provider_profile:
        profile_id = user.provider_profile.id

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "profile_id": profile_id
    }


@router.get("/me")
def get_my_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns full profile details for the authenticated user.
    """
    data = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role
    }

    if current_user.role == "student" and current_user.student_profile:
        sp = current_user.student_profile
        data["student_profile"] = {
            "id": sp.id,
            "college_name": sp.college_name,
            "hostel_area": sp.hostel_area,
            "meal_preference": sp.meal_preference
        }
    elif current_user.role == "provider" and current_user.provider_profile:
        pp = current_user.provider_profile
        data["provider_profile"] = {
            "id": pp.id,
            "service_name": pp.service_name,
            "owner_name": pp.owner_name,
            "area": pp.area,
            "food_type": pp.food_type,
            "single_meal_price": pp.single_meal_price,
            "monthly_price": pp.monthly_price,
            "is_available": pp.is_available,
            "leave_notice": pp.leave_notice
        }

    return data



@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """
    Step 1 of password reset: user submits their email.
    If the email exists, generate a one-time reset token and send (print) the reset link.
    Always returns 200 to avoid leaking whether an email exists.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        # Invalidate any existing unused tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).delete()
        db.commit()

        token_str = create_password_reset_token(user.id, db)
        base_url = str(request.base_url).rstrip("/")
        reset_url = f"{base_url}/reset-password.html?token={token_str}"
        send_reset_email(user.email, reset_url)

    return {"message": "If that email is registered, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Step 2 of password reset: user submits the token from email + their new password.
    Validates the token, updates the password, and marks the token as used.
    """
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == payload.token,
        PasswordResetToken.used == False
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or already used reset link.")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset link has expired. Please request a new one.")

    # Update password
    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password_hash = hash_password(payload.new_password)
    record.used = True
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.post("/logout")
def logout():
    """
    Acknowledge logout request (client will clear stored JWT token).
    """
    return {"message": "Logged out successfully."}
