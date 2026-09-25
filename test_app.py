import io
import sys
from fastapi.testclient import TestClient
from backend.main import app

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

client = TestClient(app)


def test_full_system_flow():
    print("=" * 60)
    print("RUNNING CEP TIFFIN SERVICES FULL-STACK AUTOMATED TESTS")
    print("=" * 60)

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✅ 1. Health check passed:", res.json()["status"])

    # 2. Static Pages Loading
    for page in ["/", "/index.html", "/login.html", "/register.html", "/student-dashboard.html", "/provider-dashboard.html", "/provider-profile.html", "/chat.html"]:
        p_res = client.get(page)
        assert p_res.status_code == 200, f"Failed to serve page {page}: {p_res.status_code}"
    print("✅ 2. All 7 HTML frontend pages served successfully.")

    # 3. Student Demo Login
    s_login = client.post("/api/auth/login", json={
        "username_or_email": "aarav_student",
        "password": "password123"
    })
    assert s_login.status_code == 200, f"Student login failed: {s_login.text}"
    student_token = s_login.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("✅ 3. Student demo login successful:", s_login.json()["full_name"])

    # 4. Provider Demo Login
    p_login = client.post("/api/auth/login", json={
        "username_or_email": "annapurna_tiffin",
        "password": "password123"
    })
    assert p_login.status_code == 200, f"Provider login failed: {p_login.text}"
    provider_token = p_login.json()["access_token"]
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    print("✅ 4. Provider demo login successful:", p_login.json()["full_name"])

    # 5. List and Search Providers
    providers_res = client.get("/api/providers?area=Dhankawadi")
    assert providers_res.status_code == 200
    providers = providers_res.json()
    assert len(providers) > 0, "No providers found for Dhankawadi"
    annapurna = next((p for p in providers if "Annapurna" in p["service_name"]), providers[0])
    annapurna_id = annapurna["id"]
    print(f"✅ 5. Provider discovery & search passed: Found {len(providers)} providers in Dhankawadi.")

    # 6. View Provider Profile Details
    p_detail = client.get(f"/api/providers/{annapurna_id}")
    assert p_detail.status_code == 200
    assert p_detail.json()["service_name"] == annapurna["service_name"]
    print("✅ 6. Provider profile details retrieved successfully.")

    # 7. Menu Management (Provider Flow)
    # 7a. Get Menu
    menu_res = client.get(f"/api/providers/{annapurna_id}/menu")
    assert menu_res.status_code == 200
    initial_menu_count = len(menu_res.json())

    # 7b. Provider adds a new dish
    new_dish = client.post("/api/providers/menu", headers=provider_headers, json={
        "name": "Puran Poli Festive Feast",
        "description": "2 Fresh Puran Polis with pure ghee, Katachi Aamti, Batata Bhaji, Rice",
        "meal_type": "Lunch",
        "category": "Veg",
        "price": 110.0,
        "is_available": True
    })
    assert new_dish.status_code == 200, f"Add dish failed: {new_dish.text}"
    dish_id = new_dish.json()["id"]
    print(f"✅ 7. Menu Item added successfully: '{new_dish.json()['name']}' (ID: {dish_id})")

    # 7c. Provider updates the dish
    update_dish = client.put(f"/api/menu/{dish_id}", headers=provider_headers, json={
        "price": 115.0
    })
    assert update_dish.status_code == 200
    assert update_dish.json()["price"] == 115.0
    print("✅ 8. Menu Item updated successfully (price updated to ₹115).")

    # 7d. Provider deletes the temporary dish
    del_dish = client.delete(f"/api/menu/{dish_id}", headers=provider_headers)
    assert del_dish.status_code == 200
    print("✅ 9. Menu Item deleted successfully.")

    # 8. Daily Hygiene Update Upload
    fake_image = io.BytesIO(b"fake_image_bytes_for_testing")
    hygiene_res = client.post(
        "/api/providers/hygiene",
        headers=provider_headers,
        data={"title": "Sanitized Stainless Steel Kitchen", "description": "Morning sanitization complete"},
        files={"image_file": ("test_hygiene.jpg", fake_image, "image/jpeg")}
    )
    assert hygiene_res.status_code == 200, f"Hygiene upload failed: {hygiene_res.text}"
    print("✅ 10. Daily Hygiene Photo upload passed:", hygiene_res.json()["title"])

    # 9. Availability and Leave Pre-Notice (Alert broadcast)
    avail_res = client.post("/api/providers/availability", headers=provider_headers, json={
        "is_available": False,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "reason_message": "Kitchen maintenance and deep cleaning"
    })
    assert avail_res.status_code == 200
    print(f"✅ 11. Provider availability & leave alert updated. Notified: {avail_res.json()['students_notified']} students.")

    # Reset availability back to online
    client.post("/api/providers/availability", headers=provider_headers, json={
        "is_available": True,
        "start_date": None,
        "end_date": None,
        "reason_message": "Back online and cooking fresh!"
    })

    # 10. Advertisements
    ad_res = client.post("/api/providers/advertisements", headers=provider_headers, data={
        "title": "Weekend Student Discount 15% Off",
        "description": "Valid on all student mess cards this weekend",
        "banner_type": "offer"
    })
    assert ad_res.status_code == 200
    ad_id = ad_res.json()["id"]
    print("✅ 12. Advertisement created successfully:", ad_res.json()["title"])

    # Check active advertisements
    all_ads = client.get("/api/advertisements")
    assert all_ads.status_code == 200
    assert any(a["id"] == ad_id for a in all_ads.json())

    # 11. Customer Subscription (Customer Count)
    sub_res = client.post(
        f"/api/providers/{annapurna_id}/subscribe",
        headers=student_headers,
        json={"provider_id": annapurna_id, "plan_type": "Monthly Lunch & Dinner", "notes": "Dhankawadi Hostel"}
    )
    assert sub_res.status_code == 200
    print("✅ 13. Student subscribed to tiffin service. Active customer registered.")

    # Provider views customer directory
    cust_res = client.get("/api/providers/dashboard/customers", headers=provider_headers)
    assert cust_res.status_code == 200
    print(f"✅ 14. Provider Customer Directory verified ({len(cust_res.json())} active customers).")

    # 12. Direct Chat (Student -> Provider -> Student)
    conv_res = client.post(f"/api/conversations?provider_id={annapurna_id}", headers=student_headers)
    assert conv_res.status_code == 200
    conv_id = conv_res.json()["id"]

    # Student sends message
    send_res1 = client.post(f"/api/conversations/{conv_id}/messages", headers=student_headers, json={
        "message_text": "Hello Tai, is lunch ready for pickup?"
    })
    assert send_res1.status_code == 200
    print("✅ 15. Student sent direct chat message:", send_res1.json()["message_text"])

    # Provider replies
    send_res2 = client.post(f"/api/conversations/{conv_id}/messages", headers=provider_headers, json={
        "message_text": "Yes beta, your hot thali is packed and ready!"
    })
    assert send_res2.status_code == 200
    print("✅ 16. Provider replied to student message:", send_res2.json()["message_text"])

    # Read messages
    msgs = client.get(f"/api/conversations/{conv_id}/messages", headers=student_headers)
    assert msgs.status_code == 200
    assert len(msgs.json()) >= 2
    print(f"✅ 17. Conversation message thread retrieved ({len(msgs.json())} messages).")

    # 13. Student Registration with role validation
    import time
    unique_suffix = int(time.time())
    new_student = client.post("/api/auth/register", json={
        "email": f"rohit_{unique_suffix}@college.edu",
        "username": f"rohit_{unique_suffix}",
        "password": "password123",
        "full_name": "Rohit Verma",
        "phone": "9823456789",
        "role": "student",
        "college_name": "PICT Pune",
        "hostel_area": "Katraj"
    })
    assert new_student.status_code == 200, f"Student registration failed: {new_student.status_code} - {new_student.text}"
    rohit_token = new_student.json()["access_token"]
    rohit_headers = {"Authorization": f"Bearer {rohit_token}"}
    print("✅ 18. New student user registered with role-based profile.")

    # Rohit posts a rating for provider 3 (HomeBite Tiffins)
    rev_res = client.post(
        "/api/providers/3/ratings",
        headers=rohit_headers,
        data={
            "rating": 5,
            "review_text": "Excellent homely taste and prompt delivery at Katraj hostel!",
            "food_quality_score": 5,
            "hygiene_score": 5
        }
    )
    assert rev_res.status_code == 200, f"Review failed: {rev_res.text}"
    print("✅ 19. Genuine student review submitted with rating calculations.")

    # 14. Notifications check
    notif_res = client.get("/api/notifications", headers=student_headers)
    assert notif_res.status_code == 200
    print(f"✅ 20. Student notifications checked ({len(notif_res.json())} notifications).")

    print("=" * 60)
    print("ALL 20 CEP PROJECT AUTOMATED SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_full_system_flow()
