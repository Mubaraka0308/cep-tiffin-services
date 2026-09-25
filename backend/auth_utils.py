import os
import smtplib
from email.message import EmailMessage
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import bcrypt

from backend.database import get_db
from backend.models import User, PasswordResetToken

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "college_cep_tiffin_services_secret_key_2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Passwords must NEVER be stored in plain text.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches the stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JSON Web Token (JWT) containing user identification and role.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates the current logged-in user from the Bearer JWT token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token.")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User account not found.")
    return user


def require_role(allowed_role: str):
    """
    Dependency factory to enforce role-based access control (RBAC).
    Ensures students cannot perform provider operations and vice-versa.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: this action requires '{allowed_role}' role."
            )
        return current_user
    return role_checker


def send_reset_email(to_email: str, reset_url: str):
    """
    Sends the password reset link through Gmail SMTP.
    """

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_username)

    if not smtp_username or not smtp_password:
        print("[EMAIL ERROR] SMTP credentials are not configured.")
        print(f"[Password Reset] Reset URL: {reset_url}")
        return

    message = EmailMessage()
    message["Subject"] = "CEP Tiffin Services - Password Reset"
    message["From"] = smtp_from
    message["To"] = to_email

    message.set_content(
        f"""Hello,

We received a request to reset your CEP Tiffin Services password.

Click the link below to reset your password:

{reset_url}

This link will expire after 1 hour and can only be used once.

If you did not request a password reset, you can safely ignore this email.

Regards,
CEP Tiffin Services
"""
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        print(f"[EMAIL] Password reset email sent to {to_email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Could not send reset email: {e}")
        print(f"[Password Reset] Reset URL: {reset_url}")


def create_password_reset_token(user_id: int, db: Session) -> str:
    """Create a password reset token record and return the raw token string."""
    import uuid
    token_str = uuid.uuid4().hex
    expires_at = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(
        user_id=user_id,
        token=token_str,
        expires_at=expires_at,
        used=False,
    )
    db.add(prt)
    db.commit()
    db.refresh(prt)
    return token_str

