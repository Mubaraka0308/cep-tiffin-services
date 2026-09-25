from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, Date, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    """
    Stores authentication and basic user accounts (Students & Providers).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False)  # 'student' or 'provider'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete")
    provider_profile = relationship("Provider", back_populates="user", uselist=False, cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete")


class Student(Base):
    """
    Stores student-specific profile information.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    college_name = Column(String(150), nullable=True, default="Pune College / University")
    hostel_area = Column(String(100), nullable=True, default="Dhankawadi")
    meal_preference = Column(String(50), nullable=True, default="veg")  # 'veg', 'non-veg', 'both', 'jain'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    ratings = relationship("Rating", back_populates="student")
    subscriptions = relationship("CustomerSubscription", back_populates="student")
    conversations = relationship("Conversation", back_populates="student")


class Provider(Base):
    """
    Stores tiffin provider/mess profile information.
    """
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    service_name = Column(String(150), nullable=False)  # e.g., "Annapurna Tiffin Services"
    owner_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    area = Column(String(100), nullable=False, default="Dhankawadi, Pune")
    full_address = Column(String(255), nullable=True)
    contact_number = Column(String(20), nullable=False)
    food_type = Column(String(50), default="Pure Veg")  # 'Pure Veg', 'Veg & Non-Veg', 'Jain'
    single_meal_price = Column(Float, default=80.0)     # Based on provider survey (₹60 - ₹120)
    monthly_price = Column(Float, default=2400.0)       # Monthly subscription
    delivery_available = Column(Boolean, default=True)
    profile_image = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)
    leave_notice = Column(Text, nullable=True)
    leave_start = Column(Date, nullable=True)
    leave_end = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="provider_profile")
    menu_items = relationship("MenuItem", back_populates="provider", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="provider", cascade="all, delete-orphan")
    hygiene_updates = relationship("HygieneUpdate", back_populates="provider", cascade="all, delete-orphan")
    availability_logs = relationship("AvailabilityLog", back_populates="provider", cascade="all, delete-orphan")
    advertisements = relationship("Advertisement", back_populates="provider", cascade="all, delete-orphan")
    subscriptions = relationship("CustomerSubscription", back_populates="provider", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="provider", cascade="all, delete-orphan")


class MenuItem(Base):
    """
    Stores dishes/meals offered by a provider.
    """
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Maharashtrian Special Thali"
    description = Column(Text, nullable=True)   # "4 Chapatis, Dal, Sabzi, Rice, Gulab Jamun"
    meal_type = Column(String(50), default="Lunch")  # "Lunch", "Dinner", "Breakfast", "All Day"
    category = Column(String(50), default="Veg")    # "Veg", "Non-Veg", "Special", "Jain"
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    provider = relationship("Provider", back_populates="menu_items")


class Rating(Base):
    """
    Stores genuine student ratings and reviews with optional photo proof.
    """
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5 stars
    review_text = Column(Text, nullable=False)
    proof_image = Column(String(255), nullable=True)  # Student meal verification image
    food_quality_score = Column(Integer, nullable=True, default=5)
    hygiene_score = Column(Integer, nullable=True, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="ratings")
    student = relationship("Student", back_populates="ratings")


class HygieneUpdate(Base):
    """
    Stores daily kitchen and preparation hygiene photos posted by providers.
    """
    __tablename__ = "hygiene_updates"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255), nullable=False)
    title = Column(String(120), default="Daily Kitchen Hygiene Photo")
    description = Column(Text, nullable=True)
    date_posted = Column(DateTime, default=datetime.utcnow)
    disclaimer = Column(String(255), default="Provider-submitted hygiene update")

    # Relationship
    provider = relationship("Provider", back_populates="hygiene_updates")


class AvailabilityLog(Base):
    """
    Tracks provider availability changes and advance leave pre-notices.
    """
    __tablename__ = "availability_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    is_available = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    reason_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    provider = relationship("Provider", back_populates="availability_logs")


class Advertisement(Base):
    """
    Promotional banners and announcements created by providers for students.
    """
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    banner_type = Column(String(50), default="offer")  # 'offer', 'announcement', 'discount'
    is_active = Column(Boolean, default=True)
    valid_until = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    provider = relationship("Provider", back_populates="advertisements")


class CustomerSubscription(Base):
    """
    Stores student subscribers/customers for each provider, providing accurate customer count.
    """
    __tablename__ = "customer_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    plan_type = Column(String(80), default="Monthly Lunch & Dinner")
    status = Column(String(30), default="active")  # 'active', 'paused', 'completed'
    start_date = Column(Date, default=date.today)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="subscriptions")
    student = relationship("Student", back_populates="subscriptions")


class Conversation(Base):
    """
    Direct chat thread between a student and a provider.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="conversations")
    provider = relationship("Provider", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """
    Individual chat messages sent inside a conversation.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")


class PasswordResetToken(Base):
    """
    Stores one-time password reset tokens for the 'forgot password' flow.
    Each token expires after 1 hour and can only be used once.
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="password_reset_tokens")


class Notification(Base):
    """
    Alerts for students and providers (leave notices, new messages, reviews).
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="general")  # 'availability_alert', 'chat_message', 'review'
    is_read = Column(Boolean, default=False)
    link_url = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="notifications")
