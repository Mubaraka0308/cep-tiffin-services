/**
 * Khane ki Khoj - Tiffin Services
 * Provider Dashboard Script: Profile, Menu, Hygiene, Leave Prenotice, Ads, Customers
 */

let providerData = null;
let currentEditingMenuItemId = null;

document.addEventListener("DOMContentLoaded", () => {
  const user = getUser();
  if (!user || user.role !== "provider") {
    showToast("Access restricted: Please log in with a provider account.", "error");
    setTimeout(() => window.location.href = "/login.html", 500);
    return;
  }

  // Setup tab switcher
  setupTabs();

  // Load all dashboard sections
  loadProviderProfileAndStats();
  loadMenuItems();
  loadHygieneSection();
  loadAvailabilitySection();
  loadCustomersList();
  loadAdvertisementsList();
  loadReviewsList();

  // Setup modals and form submissions
  setupMenuModals();
  setupHygieneUpload();
  setupAvailabilityForm();
  setupAdForm();
  setupProfileEditForm();
});

// ================= Tab Switching =================
function setupTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetTab);
      if (targetContent) targetContent.classList.add("active");
    });
  });
}

// ================= Load Profile & Key Metrics =================
async function loadProviderProfileAndStats() {
  try {
    const stats = await apiGet("/api/providers/dashboard/stats");
    providerData = await apiGet("/api/providers/current/me");

    // Update Header
    document.getElementById("provider-name-display").innerText = stats.service_name;
    document.getElementById("provider-status-text").innerText = stats.is_available ? "Online / Accepting Orders" : "Currently Unavailable";
    document.getElementById("provider-status-badge").className = `badge ${stats.is_available ? 'badge-veg' : 'badge-nonveg'}`;

    // Update Metric Cards
    document.getElementById("stat-customers-count").innerText = stats.active_customers;
    document.getElementById("stat-rating-display").innerText = `⭐ ${stats.average_rating} (${stats.total_reviews})`;
    document.getElementById("stat-menu-count").innerText = stats.total_menu_items;

    // Fill profile editor form
    if (providerData) {
      document.getElementById("edit-service-name").value = providerData.service_name || "";
      document.getElementById("edit-owner-name").value = providerData.owner_name || "";
      document.getElementById("edit-area").value = providerData.area || "";
      document.getElementById("edit-phone").value = providerData.contact_number || "";
      document.getElementById("edit-food-type").value = providerData.food_type || "Pure Veg";
      document.getElementById("edit-meal-price").value = providerData.single_meal_price || 80;
      document.getElementById("edit-monthly-price").value = providerData.monthly_price || 2400;
      document.getElementById("edit-desc").value = providerData.description || "";
      document.getElementById("edit-address").value = providerData.full_address || "";
    }
  } catch (err) {
    showToast("Failed to load provider metrics: " + err.message, "error");
  }
}

// ================= Menu Management =================
async function loadMenuItems() {
  const container = document.getElementById("provider-menu-grid");
  if (!container) return;

  try {
    if (!providerData) {
      providerData = await apiGet("/api/providers/current/me");
    }
    const items = await apiGet(`/api/providers/${providerData.id}/menu`);

    if (!items || items.length === 0) {
      container.innerHTML = `
        <div style="grid-column:1/-1; text-align:center; padding:30px; color:var(--dark-muted);">
          No menu items added yet. Click <strong>"Add New Dish"</strong> to create your first meal!
        </div>
      `;
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="menu-card">
        <div class="menu-card-header">
          <span class="badge ${item.category.includes('Veg') ? 'badge-veg' : 'badge-nonveg'}">${item.category}</span>
          <span class="badge" style="background:#f1f5f9; color:var(--dark);">${item.meal_type}</span>
        </div>
        <div class="menu-card-title">${item.name}</div>
        <div class="menu-card-price">₹${item.price}</div>
        <div class="menu-card-desc">${item.description || 'Fresh daily preparation'}</div>
        <div style="font-size:12px; margin-bottom:8px;">
          Status: <strong>${item.is_available ? '✅ Available' : '❌ Sold Out'}</strong>
        </div>
        <div class="menu-card-actions">
          <button class="btn btn-outline btn-sm" onclick="openEditMenuModal(${JSON.stringify(item).replace(/"/g, '&quot;')})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteMenuItem(${item.id})">Delete</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

function setupMenuModals() {
  const modal = document.getElementById("menu-modal");
  const form = document.getElementById("menu-form");
  const cancelBtn = document.getElementById("menu-cancel-btn");
  const closeBtn = document.getElementById("menu-close-btn");
  const addBtn = document.getElementById("add-menu-btn");

  if (!modal || !form) return;

  const closeModal = () => {
    modal.classList.remove("active");
    currentEditingMenuItemId = null;
    form.reset();
  };

  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  if (addBtn) {
    addBtn.addEventListener("click", () => {
      currentEditingMenuItemId = null;
      document.getElementById("menu-modal-title").innerText = "Add New Dish / Thali";
      form.reset();
      modal.classList.add("active");
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById("menu-item-name").value.trim(),
      description: document.getElementById("menu-item-desc").value.trim(),
      meal_type: document.getElementById("menu-item-meal-type").value,
      category: document.getElementById("menu-item-category").value,
      price: parseFloat(document.getElementById("menu-item-price").value),
      is_available: document.getElementById("menu-item-available").checked
    };

    try {
      if (currentEditingMenuItemId) {
        await apiPut(`/api/menu/${currentEditingMenuItemId}`, payload);
        showToast("Menu item updated!", "success");
      } else {
        await apiPost("/api/providers/menu", payload);
        showToast("Dish added to menu!", "success");
      }
      closeModal();
      loadMenuItems();
      loadProviderProfileAndStats();
    } catch (err) {
      showToast(err.message || "Failed to save menu item.", "error");
    }
  });
}

window.openEditMenuModal = function(item) {
  currentEditingMenuItemId = item.id;
  document.getElementById("menu-modal-title").innerText = "Edit Dish Details";
  document.getElementById("menu-item-name").value = item.name;
  document.getElementById("menu-item-desc").value = item.description || "";
  document.getElementById("menu-item-meal-type").value = item.meal_type;
  document.getElementById("menu-item-category").value = item.category;
  document.getElementById("menu-item-price").value = item.price;
  document.getElementById("menu-item-available").checked = item.is_available;

  document.getElementById("menu-modal").classList.add("active");
};

window.deleteMenuItem = async function(itemId) {
  if (!confirm("Are you sure you want to remove this dish from your active menu?")) return;
  try {
    await apiDelete(`/api/menu/${itemId}`);
    showToast("Dish deleted from menu.", "info");
    loadMenuItems();
    loadProviderProfileAndStats();
  } catch (err) {
    showToast(err.message || "Failed to delete item.", "error");
  }
};

// ================= Daily Hygiene Update =================
async function loadHygieneSection() {
  if (!providerData) return;
  try {
    const today = await apiGet(`/api/providers/${providerData.id}/hygiene/today`);
    const previewContainer = document.getElementById("hygiene-current-preview");
    if (!previewContainer) return;

    if (today.has_update) {
      previewContainer.innerHTML = `
        <img src="${today.image_path}" class="hygiene-preview-img" alt="Today's Hygiene Proof">
        <div style="margin-top:12px;">
          <h4 style="font-size:15px; font-weight:700;">${today.title}</h4>
          <p style="font-size:13px; color:var(--dark-muted);">${today.description || 'Kitchen sanitization verified.'}</p>
          <div style="font-size:11px; color:#16a34a; margin-top:4px;">
            Uploaded at: ${new Date(today.date_posted).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', month:'short', day:'numeric'})}
          </div>
        </div>
      `;
    } else {
      previewContainer.innerHTML = `
        <div style="height:220px; border:2px dashed var(--border); border-radius:var(--radius-md); display:flex; align-items:center; justify-content:center; flex-direction:column; color:var(--dark-muted);">
          <span style="font-size:36px; margin-bottom:8px;">🧼</span>
          <p>No hygiene photo uploaded today yet.</p>
          <span style="font-size:12px;">Upload a quick photo of your clean kitchen counter below!</span>
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
  }
}

function setupHygieneUpload() {
  const form = document.getElementById("hygiene-upload-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("hygiene-file");
    const titleInput = document.getElementById("hygiene-title");
    const descInput = document.getElementById("hygiene-desc");
    const submitBtn = form.querySelector("button[type='submit']");

    if (!fileInput.files || fileInput.files.length === 0) {
      showToast("Please choose an image file to upload.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("image_file", fileInput.files[0]);
    formData.append("title", titleInput.value.trim() || "Daily Kitchen & Food Prep Hygiene");
    formData.append("description", descInput.value.trim());

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = "Uploading Proof...";
      await apiUpload("/api/providers/hygiene", formData);
      showToast("Daily hygiene update published! Students can view today's proof.", "success");
      form.reset();
      loadHygieneSection();
    } catch (err) {
      showToast(err.message || "Failed to upload hygiene photo.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = "Publish Daily Hygiene Proof";
    }
  });
}

// ================= Availability & Advance Leave Prenotice =================
async function loadAvailabilitySection() {
  if (!providerData) return;
  try {
    const avail = await apiGet(`/api/providers/${providerData.id}/availability`);
    const statusRadioAvail = document.getElementById("avail-status-online");
    const statusRadioUnavail = document.getElementById("avail-status-offline");
    const startDateInput = document.getElementById("leave-start-date");
    const endDateInput = document.getElementById("leave-end-date");
    const reasonInput = document.getElementById("leave-reason");

    if (avail.is_available) {
      if (statusRadioAvail) statusRadioAvail.checked = true;
    } else {
      if (statusRadioUnavail) statusRadioUnavail.checked = true;
    }

    if (startDateInput && avail.leave_start) startDateInput.value = avail.leave_start;
    if (endDateInput && avail.leave_end) endDateInput.value = avail.leave_end;
    if (reasonInput && avail.leave_notice) reasonInput.value = avail.leave_notice;
  } catch (err) {
    console.error(err);
  }
}

function setupAvailabilityForm() {
  const form = document.getElementById("availability-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isAvail = document.getElementById("avail-status-online").checked;
    const startDate = document.getElementById("leave-start-date").value || null;
    const endDate = document.getElementById("leave-end-date").value || null;
    const reason = document.getElementById("leave-reason").value.trim() || null;
    const submitBtn = form.querySelector("button[type='submit']");

    const payload = {
      is_available: isAvail,
      start_date: startDate,
      end_date: endDate,
      reason_message: reason
    };

    try {
      submitBtn.disabled = true;
      const res = await apiPost("/api/providers/availability", payload);
      showToast(`Status updated! ${res.students_notified} connected students were notified.`, "success");
      loadProviderProfileAndStats();
    } catch (err) {
      showToast(err.message || "Failed to update availability.", "error");
    } finally {
      submitBtn.disabled = false;
    }
  });
}

// ================= Customer Directory & Count =================
async function loadCustomersList() {
  const tableBody = document.getElementById("customers-table-body");
  if (!tableBody) return;

  try {
    const customers = await apiGet("/api/providers/dashboard/customers");

    if (!customers || customers.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding:30px; color:var(--dark-muted);">
            No students currently subscribed. When students order a monthly subscription, they will appear here.
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = customers.map((c, idx) => `
      <tr>
        <td><strong>#${idx + 1}</strong></td>
        <td>
          <div style="font-weight:600;">${c.student_name}</div>
          <div style="font-size:12px; color:var(--dark-muted);">📍 ${c.student_area || 'Dhankawadi'}</div>
        </td>
        <td>${c.student_phone || '98XXXXXXXX'}</td>
        <td><span class="badge" style="background:#eff6ff; color:#1d4ed8;">${c.plan_type}</span></td>
        <td><span class="badge badge-veg">${c.status.toUpperCase()}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

// ================= Advertisements Manager =================
async function loadAdvertisementsList() {
  const container = document.getElementById("ads-list-container");
  if (!container || !providerData) return;

  try {
    const ads = await apiGet(`/api/providers/${providerData.id}/advertisements`);

    if (!ads || ads.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:20px; color:var(--dark-muted);">
          No active advertisements. Post a discount or announcement to attract new hostel students!
        </div>
      `;
      return;
    }

    container.innerHTML = ads.map(a => `
      <div style="border:1px solid var(--border); border-radius:var(--radius-sm); padding:16px; margin-bottom:12px; background:#fdfbf7;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h4 style="font-weight:700; color:var(--dark);">${a.title}</h4>
            <p style="font-size:13px; color:var(--dark-muted); margin-top:4px;">${a.description}</p>
          </div>
          <button class="btn btn-danger btn-sm" onclick="deleteAdvertisement(${a.id})">Delete</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

function setupAdForm() {
  const form = document.getElementById("advertisement-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("ad-title").value.trim();
    const desc = document.getElementById("ad-desc").value.trim();
    const bannerType = document.getElementById("ad-type").value;
    const validUntil = document.getElementById("ad-valid-until").value;
    const fileInput = document.getElementById("ad-image-file");

    const formData = new FormData();
    formData.append("title", title);
    formData.append("description", desc);
    formData.append("banner_type", bannerType);
    if (validUntil) formData.append("valid_until", validUntil);
    if (fileInput.files && fileInput.files.length > 0) {
      formData.append("image_file", fileInput.files[0]);
    }

    try {
      await apiUpload("/api/providers/advertisements", formData);
      showToast("Advertisement published to student dashboard!", "success");
      form.reset();
      loadAdvertisementsList();
    } catch (err) {
      showToast(err.message || "Failed to publish advertisement.", "error");
    }
  });
}

window.deleteAdvertisement = async function(adId) {
  if (!confirm("Are you sure you want to remove this advertisement?")) return;
  try {
    await apiDelete(`/api/advertisements/${adId}`);
    showToast("Advertisement removed.", "info");
    loadAdvertisementsList();
  } catch (err) {
    showToast(err.message, "error");
  }
};

// ================= Reviews & Student Proofs =================
async function loadReviewsList() {
  const container = document.getElementById("provider-reviews-list");
  if (!container || !providerData) return;

  try {
    const res = await apiGet(`/api/providers/${providerData.id}/ratings`);
    document.getElementById("weekly-avg-display").innerText = `⭐ ${res.weekly_average_rating}`;
    document.getElementById("weekly-count-display").innerText = `${res.weekly_reviews_count} reviews this week`;

    if (!res.reviews || res.reviews.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:30px; color:var(--dark-muted);">
          No reviews received yet.
        </div>
      `;
      return;
    }

    container.innerHTML = res.reviews.map(r => `
      <div style="border-bottom:1px solid var(--border-light); padding:16px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <strong>${r.student_name} (${r.student_college || 'Student'})</strong>
          <span class="badge badge-rating">⭐ ${r.rating} / 5</span>
        </div>
        <p style="font-size:14px; color:var(--dark); margin:6px 0;">"${r.review_text}"</p>
        ${r.proof_image ? `
          <div style="margin-top:8px;">
            <span style="font-size:11px; color:var(--dark-muted);">📷 Student Meal Proof:</span><br>
            <img src="${r.proof_image}" style="width:120px; height:80px; object-fit:cover; border-radius:6px; margin-top:4px;" alt="Meal Proof">
          </div>
        ` : ''}
        <div style="font-size:11px; color:var(--dark-muted); margin-top:6px;">
          Reviewed on: ${new Date(r.created_at).toLocaleDateString()}
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

// ================= Profile Edit Form =================
function setupProfileEditForm() {
  const form = document.getElementById("profile-edit-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      service_name: document.getElementById("edit-service-name").value.trim(),
      owner_name: document.getElementById("edit-owner-name").value.trim(),
      area: document.getElementById("edit-area").value.trim(),
      contact_number: document.getElementById("edit-phone").value.trim(),
      food_type: document.getElementById("edit-food-type").value,
      single_meal_price: parseFloat(document.getElementById("edit-meal-price").value),
      monthly_price: parseFloat(document.getElementById("edit-monthly-price").value),
      description: document.getElementById("edit-desc").value.trim(),
      full_address: document.getElementById("edit-address").value.trim()
    };

    try {
      await apiPut("/api/providers/current/me", payload);
      showToast("Profile details updated successfully!", "success");
      loadProviderProfileAndStats();
    } catch (err) {
      showToast(err.message || "Failed to update profile.", "error");
    }
  });
}
