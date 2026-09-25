/**
 * Khane ki Khoj - Tiffin Services
 * Authentication Script: Login & Registration Handlers
 */

document.addEventListener("DOMContentLoaded", () => {
  initLoginForm();
  initRegisterForm();
});

// ================= Login Handler =================
function initLoginForm() {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  // Check URL parameters for session expiry notice
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("expired")) {
    showToast("Your session has expired. Please log in again.", "info");
  }

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = loginForm.querySelector("button[type='submit']");
    const errorAlert = document.getElementById("login-error-alert");

    if (errorAlert) errorAlert.style.display = "none";

    const usernameOrEmail = document.getElementById("username_or_email").value.trim();
    const password = document.getElementById("password").value;

    if (!usernameOrEmail || !password) {
      if (errorAlert) {
        errorAlert.innerText = "Please fill in all fields.";
        errorAlert.style.display = "block";
      }
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = "Signing in...";

      const res = await apiPost("/api/auth/login", {
        username_or_email: usernameOrEmail,
        password: password
      });

      setUserSession(res);
      showToast(`Welcome back, ${res.full_name}!`, "success");

      setTimeout(() => {
        if (res.role === "provider") {
          window.location.href = "/provider-dashboard.html";
        } else {
          window.location.href = "/student-dashboard.html";
        }
      }, 600);

    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.innerText = "Login to Account";
      if (errorAlert) {
        errorAlert.innerText = err.message || "Invalid credentials.";
        errorAlert.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  });
}

// ================= Registration Handler =================
function initRegisterForm() {
  const registerForm = document.getElementById("register-form");
  if (!registerForm) return;

  const roleStudentRadio = document.getElementById("role-student");
  const roleProviderRadio = document.getElementById("role-provider");
  const studentFields = document.getElementById("student-fields");
  const providerFields = document.getElementById("provider-fields");

  // Toggle role fields dynamically
  function updateRoleVisibility() {
    const isStudent = roleStudentRadio ? roleStudentRadio.checked : true;
    if (studentFields) studentFields.style.display = isStudent ? "block" : "none";
    if (providerFields) providerFields.style.display = isStudent ? "none" : "block";
  }

  if (roleStudentRadio) roleStudentRadio.addEventListener("change", updateRoleVisibility);
  if (roleProviderRadio) roleProviderRadio.addEventListener("change", updateRoleVisibility);
  updateRoleVisibility();

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = registerForm.querySelector("button[type='submit']");
    const errorAlert = document.getElementById("register-error-alert");

    if (errorAlert) errorAlert.style.display = "none";

    const role = (roleProviderRadio && roleProviderRadio.checked) ? "provider" : "student";
    const fullName = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const username = document.getElementById("reg-username").value.trim();
    const phone = document.getElementById("reg-phone").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirmPass = document.getElementById("reg-confirm-password").value;

    if (password !== confirmPass) {
      if (errorAlert) {
        errorAlert.innerText = "Passwords do not match.";
        errorAlert.style.display = "block";
      }
      return;
    }

    const payload = {
      role: role,
      full_name: fullName,
      email: email,
      username: username,
      phone: phone,
      password: password
    };

    if (role === "student") {
      payload.college_name = document.getElementById("reg-college")?.value.trim() || "Pune College";
      payload.hostel_area = document.getElementById("reg-area")?.value.trim() || "Dhankawadi";
      payload.meal_preference = document.getElementById("reg-preference")?.value || "veg";
    } else {
      payload.service_name = document.getElementById("reg-service-name")?.value.trim() || `${fullName}'s Tiffins`;
      payload.area = document.getElementById("reg-provider-area")?.value.trim() || "Dhankawadi, Pune";
      payload.food_type = document.getElementById("reg-food-type")?.value || "Pure Veg";
      payload.single_meal_price = parseFloat(document.getElementById("reg-meal-price")?.value || "80");
      payload.monthly_price = parseFloat(document.getElementById("reg-monthly-price")?.value || "2400");
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = "Creating Account...";

      const res = await apiPost("/api/auth/register", payload);
      setUserSession(res);
      showToast("Account created successfully! Welcome to Khane ki Khoj.", "success");

      setTimeout(() => {
        if (res.role === "provider") {
          window.location.href = "/provider-dashboard.html";
        } else {
          window.location.href = "/student-dashboard.html";
        }
      }, 600);

    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.innerText = "Create Account";
      if (errorAlert) {
        errorAlert.innerText = err.message || "Failed to create account.";
        errorAlert.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  });
}
