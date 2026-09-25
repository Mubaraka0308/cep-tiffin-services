from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from backend.models import (
    User, Student, Provider, MenuItem, Rating,
    HygieneUpdate, AvailabilityLog, Advertisement,
    CustomerSubscription, Conversation, Message, Notification
)
from backend.auth_utils import hash_password


def seed_demo_data(db: Session):
    """
    Populates realistic demo data based on the CEP research conducted in Pune
    (Sarita Vihar, Dhankawadi, Katraj) as documented in the project presentation.
    """
    # Check if data is already seeded
    if db.query(User).count() > 0:
        return

    print("[DATABASE SEED] Seeding demo data for Pune tiffin services...")

    default_pass = hash_password("password123")

    # 1. Create Student Users
    student_user_1 = User(
        email="student1@college.edu",
        username="aarav_student",
        password_hash=default_pass,
        full_name="Aarav Sharma",
        phone="9823011223",
        role="student"
    )
    student_user_2 = User(
        email="student2@college.edu",
        username="priya_student",
        password_hash=default_pass,
        full_name="Priya Patel",
        phone="9823099887",
        role="student"
    )
    db.add_all([student_user_1, student_user_2])
    db.commit()

    student_profile_1 = Student(
        user_id=student_user_1.id,
        college_name="Pune Institute of Engineering & Technology",
        hostel_area="Dhankawadi",
        meal_preference="veg"
    )
    student_profile_2 = Student(
        user_id=student_user_2.id,
        college_name="Symbiosis International University",
        hostel_area="Sarita Vihar",
        meal_preference="both"
    )
    db.add_all([student_profile_1, student_profile_2])
    db.commit()

    # 2. Create Provider Users
    # Provider 1: Annapurna Tiffin Services (Sunita Tai) - Dhankawadi
    p1_user = User(
        email="annapurna@tiffin.com",
        username="annapurna_tiffin",
        password_hash=default_pass,
        full_name="Sunita Deshmukh",
        phone="9822456781",
        role="provider"
    )
    # Provider 2: Ghar Ka Swad Mess (Ramesh Patil) - Sarita Vihar
    p2_user = User(
        email="gharkaswad@tiffin.com",
        username="ghar_ka_swad",
        password_hash=default_pass,
        full_name="Ramesh Patil",
        phone="9822987654",
        role="provider"
    )
    # Provider 3: HomeBite Tiffins (Kavita Sharma) - Katraj
    p3_user = User(
        email="homebite@tiffin.com",
        username="homebite_tiffins",
        password_hash=default_pass,
        full_name="Kavita Sharma",
        phone="9823123456",
        role="provider"
    )
    # Provider 4: FreshBox Meals (Vikram Joshi) - Pune Central
    p4_user = User(
        email="freshbox@tiffin.com",
        username="freshbox_meals",
        password_hash=default_pass,
        full_name="Vikram Joshi",
        phone="9823654321",
        role="provider"
    )
    db.add_all([p1_user, p2_user, p3_user, p4_user])
    db.commit()

    # 3. Create Provider Profiles
    provider_1 = Provider(
        user_id=p1_user.id,
        service_name="Annapurna Tiffin Services",
        owner_name="Sunita Tai Deshmukh",
        description="Authentic Maharashtrian and North Indian daily tiffins. Prepared in home-style hygiene with fresh rotis, seasonal vegetables, and aromatic dals. Monthly lunch and dinner subscriptions available.",
        area="Dhankawadi, Pune",
        full_address="Flat 102, Sneha Heights, Near Bharati Vidyapeeth, Dhankawadi, Pune",
        contact_number="9822456781",
        food_type="Pure Veg",
        single_meal_price=80.0,
        monthly_price=2400.0,
        delivery_available=True,
        profile_image="https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
        is_available=True
    )

    leave_start = date.today() + timedelta(days=1)
    leave_end = date.today() + timedelta(days=3)
    provider_2 = Provider(
        user_id=p2_user.id,
        service_name="Ghar Ka Swad Mess",
        owner_name="Ramesh Patil",
        description="Homely student mess operating since 2018 in Sarita Vihar. Generous portions, balanced thalis, and special Sunday chicken feasts for hostel students.",
        area="Sarita Vihar, Pune",
        full_address="House 24, Lane 3, Sarita Vihar, Near Sinhgad Campus, Pune",
        contact_number="9822987654",
        food_type="Veg & Non-Veg",
        single_meal_price=75.0,
        monthly_price=2200.0,
        delivery_available=True,
        profile_image="https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80",
        is_available=False,
        leave_start=leave_start,
        leave_end=leave_end,
        leave_notice="Advance Notice: Kitchen closed due to family wedding in Kolhapur. Resuming fresh deliveries on Monday morning."
    )

    provider_3 = Provider(
        user_id=p3_user.id,
        service_name="HomeBite Tiffins",
        owner_name="Kavita Sharma",
        description="Clean, oil-controlled, wholesome food designed specifically for students who miss home food. Special Jain meals prepared with separate utensils on request.",
        area="Katraj, Pune",
        full_address="Sector 5, Near Katraj Snake Park, Pune",
        contact_number="9823123456",
        food_type="Pure Veg",
        single_meal_price=85.0,
        monthly_price=2500.0,
        delivery_available=True,
        profile_image="https://images.unsplash.com/photo-1613292443284-8d10ef9383fe?w=600&auto=format&fit=crop&q=80",
        is_available=True
    )

    provider_4 = Provider(
        user_id=p4_user.id,
        service_name="FreshBox Meals",
        owner_name="Vikram Joshi",
        description="Modern healthy student meals packed in hygienic leakproof containers. Includes salads, sprout chaat, paneer curry, and multi-grain rotis.",
        area="Bibwewadi, Pune",
        full_address="Shop 8, Lake Town Complex, Bibwewadi, Pune",
        contact_number="9823654321",
        food_type="Veg & Non-Veg",
        single_meal_price=95.0,
        monthly_price=2800.0,
        delivery_available=True,
        profile_image="https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80",
        is_available=True
    )

    db.add_all([provider_1, provider_2, provider_3, provider_4])
    db.commit()

    # 4. Create Menu Items
    menu_items = [
        # Annapurna Tiffins
        MenuItem(
            provider_id=provider_1.id,
            name="Maharashtrian Special Veg Thali",
            description="4 Hot Wheat Phulkas, Pithla / Shev Bhaji, Matki Usal, Indrayani Rice, Dal Tadka, Mirchi Thecha & Salad",
            meal_type="Lunch",
            category="Veg",
            price=80.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_1.id,
            name="North Indian Dinner Thali",
            description="3 Butter Rotis, Paneer Bhurji / Shahi Paneer, Dal Makhani, Jeera Rice, Gulab Jamun",
            meal_type="Dinner",
            category="Veg",
            price=90.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_1.id,
            name="Hostel Economical Mini Tiffin",
            description="3 Phulkas, Seasonal Mixed Sabzi, Dal Fry, Steamed Rice, Pickle",
            meal_type="All Day",
            category="Veg",
            price=65.0,
            is_available=True
        ),

        # Ghar Ka Swad
        MenuItem(
            provider_id=provider_2.id,
            name="Regular Student Daily Thali",
            description="4 Chapatis, Dal Fry, Aloo Gobi Masala, Steamed Rice, Papad & Salad",
            meal_type="Lunch",
            category="Veg",
            price=75.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_2.id,
            name="Sunday Special Chicken Thali",
            description="Kolhapuri Chicken Sukka Gravy, 3 Jowar Bhakris, Indrayani Rice, Tambda Rassa & Solkadhi",
            meal_type="Lunch",
            category="Non-Veg",
            price=130.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_2.id,
            name="Egg Curry Thali",
            description="2 Boiled Eggs in Onion-Tomato Gravy, 3 Chapatis, Steamed Rice, Salad",
            meal_type="Dinner",
            category="Non-Veg",
            price=95.0,
            is_available=True
        ),

        # HomeBite Tiffins
        MenuItem(
            provider_id=provider_3.id,
            name="Pure Jain Satvik Thali",
            description="Prepared with separate utensils without onion or garlic: 4 Ghee Phulkas, Moong Dal, Lauki Kofta, Jeera Rice",
            meal_type="Lunch",
            category="Jain",
            price=85.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_3.id,
            name="Low-Oil Homely Dinner Box",
            description="3 Soft Multigrain Rotis, Palak Paneer, Yellow Moong Dal, Steamed Brown Rice, Cucumber Salad",
            meal_type="Dinner",
            category="Veg",
            price=90.0,
            is_available=True
        ),

        # FreshBox Meals
        MenuItem(
            provider_id=provider_4.id,
            name="High-Protein Fitness Meal",
            description="200g Grilled Paneer/Soya Chunks, Sauteed Veggies, Sprout Chaat, 2 Multigrain Rotis, Dal Soup",
            meal_type="Lunch",
            category="Veg",
            price=120.0,
            is_available=True
        ),
        MenuItem(
            provider_id=provider_4.id,
            name="Balanced Student Meal Bowl",
            description="Choice of Rajma / Chole / Paneer with fragrant Rice bowl, roasted papad and mint chutney",
            meal_type="Dinner",
            category="Veg",
            price=95.0,
            is_available=True
        )
    ]
    db.add_all(menu_items)
    db.commit()

    # 5. Create Hygiene Updates (Crucial requirement from PPT!)
    hygiene_1 = HygieneUpdate(
        provider_id=provider_1.id,
        image_path="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80",
        title="Sanitized Kitchen & Fresh Morning Prep",
        description="Daily kitchen sanitization completed at 7:30 AM. All vegetables soaked and washed in purified water. Roti counter wiped with food-grade disinfectant.",
        date_posted=datetime.utcnow() - timedelta(hours=3),
        disclaimer="Provider-submitted daily hygiene update"
    )
    hygiene_2 = HygieneUpdate(
        provider_id=provider_3.id,
        image_path="https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=600&auto=format&fit=crop&q=80",
        title="Steam-Sterilized Tiffin Boxes & Kitchen Counters",
        description="Stainless steel tiffin boxes steam cleaned at 100°C before packaging. Filtered RO water used for all cooking.",
        date_posted=datetime.utcnow() - timedelta(hours=5),
        disclaimer="Provider-submitted daily hygiene update"
    )
    db.add_all([hygiene_1, hygiene_2])
    db.commit()

    # 6. Create Customer Subscriptions (Customer Count)
    sub1 = CustomerSubscription(
        provider_id=provider_1.id,
        student_id=student_profile_1.id,
        plan_type="Monthly Lunch & Dinner",
        status="active",
        notes="Deliver to PIET Boy's Hostel Gate 2, Dhankawadi"
    )
    sub2 = CustomerSubscription(
        provider_id=provider_2.id,
        student_id=student_profile_2.id,
        plan_type="Monthly Lunch Only",
        status="active",
        notes="Non-veg on Sundays preferred"
    )
    db.add_all([sub1, sub2])
    db.commit()

    # 7. Create Genuine Ratings & Reviews (With student proof)
    r1 = Rating(
        provider_id=provider_1.id,
        student_id=student_profile_1.id,
        rating=5,
        review_text="Sunita Tai's tiffin genuinely feels like home food. Rotis are super soft even when eaten 2 hours later in the hostel. Dal tadka has authentic flavor. Best tiffin in Dhankawadi area!",
        proof_image="https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
        food_quality_score=5,
        hygiene_score=5,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    r2 = Rating(
        provider_id=provider_2.id,
        student_id=student_profile_2.id,
        rating=4,
        review_text="Great food quantity and reasonable monthly price for students in Sarita Vihar. The Sunday chicken thali is unbeatable. They gave clear notice before their leave this week.",
        proof_image="https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80",
        food_quality_score=4,
        hygiene_score=4,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add_all([r1, r2])
    db.commit()

    # 8. Create Advertisements
    ad1 = Advertisement(
        provider_id=provider_1.id,
        title="🎓 Semester Special: Flat 10% Off on 3-Month Tiffin Cards",
        description="Book your monthly lunch & dinner mess subscription for 3 months and get 10% discount plus complimentary sweet every Saturday!",
        banner_type="offer",
        is_active=True,
        valid_until=date.today() + timedelta(days=30),
        image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80"
    )
    ad2 = Advertisement(
        provider_id=provider_2.id,
        title="🍗 Sunday Feast Announcement: Kolhapuri Sukka & Solkadhi",
        description="Special Non-Veg meal bookings open for this upcoming weekend. Limited 40 student slots. Reserve via direct chat!",
        banner_type="announcement",
        is_active=True,
        valid_until=date.today() + timedelta(days=7),
        image_url="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80"
    )
    db.add_all([ad1, ad2])
    db.commit()

    # 9. Create Chat Conversation & Messages
    conv1 = Conversation(
        student_id=student_profile_1.id,
        provider_id=provider_1.id,
        last_message_at=datetime.utcnow() - timedelta(minutes=25)
    )
    db.add(conv1)
    db.commit()

    msg1 = Message(
        conversation_id=conv1.id,
        sender_id=student_user_1.id,
        message_text="Namaste Sunita Tai! Could you please add extra salad and one more chapati with today's lunch tiffin?",
        is_read=True,
        created_at=datetime.utcnow() - timedelta(minutes=30)
    )
    msg2 = Message(
        conversation_id=conv1.id,
        sender_id=p1_user.id,
        message_text="Namaste Aarav beta! Yes definitely, I will pack 2 extra hot chapatis and fresh cucumber-tomato salad for you.",
        is_read=True,
        created_at=datetime.utcnow() - timedelta(minutes=25)
    )
    db.add_all([msg1, msg2])
    db.commit()

    # 10. Create Notifications
    notif1 = Notification(
        user_id=student_user_2.id,
        title="⚠️ Alert: Ghar Ka Swad Leave Notice",
        message="Ghar Ka Swad Mess will be closed from tomorrow for 3 days due to a family wedding in Kolhapur. Resuming service on Monday.",
        notification_type="availability_alert",
        link_url=f"/provider-profile.html?id={provider_2.id}",
        is_read=False,
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    notif2 = Notification(
        user_id=p1_user.id,
        title="New 5-Star Review Received! ⭐",
        message="Aarav Sharma left a glowing 5-star review: \"Sunita Tai's tiffin genuinely feels like home food...\"",
        notification_type="new_rating",
        is_read=False,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add_all([notif1, notif2])
    db.commit()

    print("[DATABASE SEED] Demo data successfully seeded!")
