/**
 * Khane ki Khoj - Tiffin Services
 * Student Dashboard Script: Provider Discovery, Search & Filters, Subscriptions
 */

let allProviders = [];

document.addEventListener("DOMContentLoaded", () => {
  const user = getUser();
  if (!user || user.role !== "student") {
    // If not a student, redirect appropriately
    if (user && user.role === "provider") {
      window.location.href = "/provider-dashboard.html";
      return;
    }
    // Allow guest browsing or redirect to login
  }

  // Set greeting
  const studentNameEl = document.getElementById("student-greeting-name");
  if (studentNameEl && user) {
    studentNameEl.innerText = user.full_name;
  }

  // Load active advertisements
  loadAdvertisementsBanner();

  // Load and render providers
  loadProviders();

  // Setup search and filter listeners
  setupFilterListeners();

  // Setup subscription modal
  setupSubscriptionModal();
});

// ================= Load Active Advertisements =================
async function loadAdvertisementsBanner() {
  const adBannerContainer = document.getElementById("ad-banner-section");
  if (!adBannerContainer) return;

  try {
    const ads = await apiGet("/api/advertisements");
    if (!ads || ads.length === 0) {
      adBannerContainer.style.display = "none";
      return;
    }

    const featuredAd = ads[0]; // Display the top current promo
    adBannerContainer.innerHTML = `
      <div class="ad-banner-card">
        <div class="ad-banner-info">
          <span class="badge" style="background:#ea580c; color:#fff; margin-bottom:8px; display:inline-block;">📢 Featured Promotion</span>
          <h3>${featuredAd.title}</h3>
          <p>${featuredAd.description}</p>
          <div style="margin-top:10px; font-size:12px; color:#9a3412;">
            Offered by: <strong>${featuredAd.provider_name}</strong>
          </div>
        </div>
        <div>
          <a href="/provider-profile.html?id=${featuredAd.provider_id}" class="btn btn-primary btn-sm">View Offer & Menu</a>
        </div>
      </div>
    `;
    adBannerContainer.style.display = "block";
  } catch (err) {
    console.error("Failed to load advertisements:", err);
  }
}

// ================= Fetch Providers =================
async function loadProviders() {
  const grid = document.getElementById("providers-grid");
  const loading = document.getElementById("providers-loading");

  if (loading) loading.style.display = "block";
  if (grid) grid.innerHTML = "";

  try {
    allProviders = await apiGet("/api/providers");
    renderProviders(allProviders);
  } catch (err) {
    if (grid) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding:40px; color:var(--danger);">
          Failed to load providers. Please check server connection.
        </div>
      `;
    }
    showToast(err.message, "error");
  } finally {
    if (loading) loading.style.display = "none";
  }
}

// ================= Render Providers Grid =================
function renderProviders(providers) {
  const grid = document.getElementById("providers-grid");
  const emptyState = document.getElementById("no-providers-found");

  if (!grid) return;
  grid.innerHTML = "";

  if (!providers || providers.length === 0) {
    if (emptyState) emptyState.style.display = "block";
    return;
  }
  if (emptyState) emptyState.style.display = "none";

  grid.innerHTML = providers.map(p => {
    const isAvail = p.is_available;
    const statusClass = isAvail ? "status-available" : "status-unavailable";
    const statusText = isAvail ? "✅ Available Today" : "⚠️ Currently Unavailable";
    const defaultImg = "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80";
    const profileImg = p.profile_image || defaultImg;

    // Leave alert box
    let leaveBox = "";
    if (!isAvail && p.leave_notice) {
      leaveBox = `
        <div class="provider-leave-alert-box">
          📢 <strong>Advance Leave Notice:</strong> ${p.leave_notice}
        </div>
      `;
    }

    // Daily hygiene indicator
    let hygieneTag = "";
    if (p.today_hygiene_image) {
      hygieneTag = `<div class="provider-hygiene-tag">🧼 Daily Hygiene Proof Posted</div>`;
    }

    return `
      <div class="provider-card">
        <div class="provider-card-img-wrap">
          <img src="${profileImg}" alt="${p.service_name}" class="provider-card-img">
          <span class="provider-status-badge ${statusClass}">${statusText}</span>
          ${hygieneTag}
        </div>
        <div class="provider-card-body">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
            <h3 class="provider-card-title">${p.service_name}</h3>
            <span class="badge badge-rating">⭐ ${p.average_rating > 0 ? p.average_rating : 'New'} (${p.rating_count})</span>
          </div>
          <div class="provider-card-area">📍 ${p.area}</div>

          <div class="provider-card-badges">
            <span class="badge ${p.food_type.includes('Veg') ? 'badge-veg' : 'badge-nonveg'}">${p.food_type}</span>
            <span class="badge" style="background:#e0f2fe; color:#0369a1;">👥 ${p.active_customer_count} Active Students</span>
            ${p.delivery_available ? '<span class="badge" style="background:#fef3c7; color:#92400e;">🛵 Delivery</span>' : ''}
          </div>

          <p style="font-size:13px; color:var(--dark-muted); margin-bottom:12px; line-height:1.4;">
            ${p.description ? p.description.slice(0, 100) + '...' : 'Wholesome student meals delivered fresh daily.'}
          </p>

          ${leaveBox}

          <div class="provider-card-footer">
            <div class="price-tag">
              From <strong>₹${p.single_meal_price}</strong> / meal
              <div style="font-size:11px; color:var(--dark-muted);">₹${p.monthly_price}/month</div>
            </div>
            <div style="display:flex; gap:6px;">
              <button class="btn btn-outline btn-sm" onclick="startDirectChat(${p.id})">💬 Chat</button>
              <a href="/provider-profile.html?id=${p.id}" class="btn btn-primary btn-sm">View Profile</a>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// ================= Search and Filters =================
function setupFilterListeners() {
  const searchInput = document.getElementById("search-input");
  const areaSelect = document.getElementById("filter-area");
  const foodTypeSelect = document.getElementById("filter-food-type");
  const maxPriceInput = document.getElementById("filter-max-price");
  const priceDisplay = document.getElementById("price-display");
  const availableOnlyCheck = document.getElementById("filter-available-only");
  const resetBtn = document.getElementById("reset-filters-btn");

  function applyFilters() {
    const searchVal = searchInput ? searchInput.value.toLowerCase().trim() : "";
    const areaVal = areaSelect ? areaSelect.value.toLowerCase() : "all";
    const foodVal = foodTypeSelect ? foodTypeSelect.value.toLowerCase() : "all";
    const maxPrice = maxPriceInput ? parseFloat(maxPriceInput.value) : 200;
    const availableOnly = availableOnlyCheck ? availableOnlyCheck.checked : false;

    if (priceDisplay && maxPriceInput) {
      priceDisplay.innerText = `₹${maxPriceInput.value}`;
    }

    const filtered = allProviders.filter(p => {
      // Search match
      if (searchVal) {
        const matchesName = p.service_name.toLowerCase().includes(searchVal);
        const matchesArea = p.area.toLowerCase().includes(searchVal);
        const matchesDesc = (p.description || "").toLowerCase().includes(searchVal);
        if (!matchesName && !matchesArea && !matchesDesc) return false;
      }

      // Area match
      if (areaVal !== "all") {
        if (!p.area.toLowerCase().includes(areaVal)) return false;
      }

      // Food type match
      if (foodVal !== "all") {
        if (!p.food_type.toLowerCase().includes(foodVal)) return false;
      }

      // Price match
      if (p.single_meal_price > maxPrice) return false;

      // Available match
      if (availableOnly && !p.is_available) return false;

      return true;
    });

    renderProviders(filtered);
  }

  if (searchInput) searchInput.addEventListener("input", applyFilters);
  if (areaSelect) areaSelect.addEventListener("change", applyFilters);
  if (foodTypeSelect) foodTypeSelect.addEventListener("change", applyFilters);
  if (maxPriceInput) maxPriceInput.addEventListener("input", applyFilters);
  if (availableOnlyCheck) availableOnlyCheck.addEventListener("change", applyFilters);

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      if (areaSelect) areaSelect.value = "all";
      if (foodTypeSelect) foodTypeSelect.value = "all";
      if (maxPriceInput) {
        maxPriceInput.value = 150;
        if (priceDisplay) priceDisplay.innerText = "₹150";
      }
      if (availableOnlyCheck) availableOnlyCheck.checked = false;
      renderProviders(allProviders);
    });
  }
}

// ================= Quick Direct Chat =================
async function startDirectChat(providerId) {
  const user = getUser();
  if (!user) {
    showToast("Please log in to start a direct chat with the provider.", "info");
    setTimeout(() => {
      window.location.href = "/login.html";
    }, 600);
    return;
  }

  try {
    const res = await apiPost(`/api/conversations?provider_id=${providerId}`);
    window.location.href = `/chat.html?conv=${res.id}`;
  } catch (err) {
    showToast(err.message || "Failed to start conversation.", "error");
  }
}

// ================= Subscribe Modal Handler =================
let selectedProviderForSub = null;

function setupSubscriptionModal() {
  const modal = document.getElementById("subscribe-modal");
  const form = document.getElementById("subscribe-form");
  const cancelBtn = document.getElementById("sub-cancel-btn");
  const closeBtn = document.getElementById("sub-close-btn");

  if (!modal || !form) return;

  const closeModal = () => modal.classList.remove("active");
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selectedProviderForSub) return;

    const planType = document.getElementById("sub-plan-type").value;
    const notes = document.getElementById("sub-notes").value.trim();

    try {
      await apiPost(`/api/providers/${selectedProviderForSub}/subscribe`, {
        provider_id: selectedProviderForSub,
        plan_type: planType,
        notes: notes
      });

      closeModal();
      showToast("Subscription submitted! The provider has been notified.", "success");
      loadProviders(); // Refresh customer count
    } catch (err) {
      showToast(err.message || "Failed to subscribe.", "error");
    }
  });
}

function openSubscribeModal(providerId, providerName) {
  const user = getUser();
  if (!user) {
    showToast("Please log in as a student to subscribe.", "info");
    setTimeout(() => window.location.href = "/login.html", 600);
    return;
  }

  selectedProviderForSub = providerId;
  const nameEl = document.getElementById("sub-provider-name");
  if (nameEl) nameEl.innerText = providerName;

  const modal = document.getElementById("subscribe-modal");
  if (modal) modal.classList.add("active");
}
