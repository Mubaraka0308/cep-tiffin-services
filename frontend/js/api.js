/**
 * Khane ki Khoj - Tiffin Services (CEP Project)
 * Central API Client and Utility Functions
 */

const API_BASE = ""; // Relative URL allows serving on same FastAPI port without CORS issues

// ================= Local Storage Auth Helpers =================
function getToken() {
  return localStorage.getItem("tiffin_token");
}

function getUser() {
  const userStr = localStorage.getItem("tiffin_user");
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
}

function setUserSession(data) {
  localStorage.setItem("tiffin_token", data.access_token);
  localStorage.setItem("tiffin_user", JSON.stringify({
    user_id: data.user_id,
    username: data.username,
    full_name: data.full_name,
    role: data.role,
    profile_id: data.profile_id
  }));
}

function clearUserSession() {
  localStorage.removeItem("tiffin_token");
  localStorage.removeItem("tiffin_user");
}

// ================= Centralized Request Utility =================
async function apiRequest(endpoint, method = "GET", data = null, isFormData = false) {
  const headers = {};
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options = {
    method: method,
    headers: headers
  };

  if (data) {
    if (isFormData) {
      options.body = data; // Browser sets multipart boundary automatically
    } else {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(data);
    }
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMsg = result.detail || result.message || "An unexpected error occurred.";
      if (response.status === 401 && !endpoint.includes("/login")) {
        clearUserSession();
        window.location.href = "/login.html?expired=true";
      }
      throw new Error(errorMsg);
    }

    return result;
  } catch (err) {
    console.error(`API Error [${method} ${endpoint}]:`, err.message);
    throw err;
  }
}

// Shortcut methods
const apiGet = (url) => apiRequest(url, "GET");
const apiPost = (url, data) => apiRequest(url, "POST", data);
const apiPut = (url, data) => apiRequest(url, "PUT", data);
const apiDelete = (url) => apiRequest(url, "DELETE");
const apiUpload = (url, formData) => apiRequest(url, "POST", formData, true);

// ================= Toast Notifications =================
function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  if (type === "error") icon = "⚠️";

  toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.4s ease";
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// ================= Common Navigation Updater =================
function updateNavigation() {
  const user = getUser();
  const navActions = document.getElementById("nav-actions");
  if (!navActions) return;

  if (user) {
    const dashboardUrl = user.role === "provider" ? "/provider-dashboard.html" : "/student-dashboard.html";
    navActions.innerHTML = `
      <div style="position: relative;">
        <button class="notification-bell-btn" id="bell-btn" title="Notifications">
          🔔
          <span class="notification-badge" id="notif-badge" style="display:none;">0</span>
        </button>
        <div class="notifications-dropdown" id="notif-dropdown">
          <div class="notif-header">
            <span>Notifications & Alerts</span>
            <button class="btn btn-sm btn-outline" id="mark-all-read-btn" style="padding:2px 8px; font-size:11px;">Mark Read</button>
          </div>
          <div id="notif-list">
            <div style="padding:16px; text-align:center; color:var(--dark-muted); font-size:13px;">No new alerts</div>
          </div>
        </div>
      </div>
      <a href="/chat.html" class="btn btn-outline btn-sm" title="Messages">💬 Chat</a>
      <button class="btn btn-danger btn-sm" onclick="handleLogout()">Logout</button>
    `;

    setupNotificationSystem();
  } else {
    navActions.innerHTML = `
      <a href="/login.html" class="btn btn-outline btn-sm">Login</a>
      <a href="/register.html" class="btn btn-primary btn-sm">Sign Up</a>
    `;
  }
}

// Notifications dropdown toggle and poller
function setupNotificationSystem() {
  const bellBtn = document.getElementById("bell-btn");
  const notifDropdown = document.getElementById("notif-dropdown");
  const markAllBtn = document.getElementById("mark-all-read-btn");

  if (bellBtn && notifDropdown) {
    bellBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle("active");
      loadNotificationsList();
    });

    document.addEventListener("click", (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== bellBtn) {
        notifDropdown.classList.remove("active");
      }
    });
  }

  if (markAllBtn) {
    markAllBtn.addEventListener("click", async () => {
      try {
        await apiPut("/api/notifications/read-all", {});
        loadNotificationsBadge();
        loadNotificationsList();
      } catch (err) {
        console.error(err);
      }
    });
  }

  loadNotificationsBadge();
  // Poll notifications badge every 15 seconds
  setInterval(loadNotificationsBadge, 15000);
}

async function loadNotificationsBadge() {
  if (!getToken()) return;
  try {
    const res = await apiGet("/api/notifications/unread-count");
    const badge = document.getElementById("notif-badge");
    if (badge) {
      if (res.unread_count > 0) {
        badge.innerText = res.unread_count;
        badge.style.display = "flex";
      } else {
        badge.style.display = "none";
      }
    }
  } catch (e) {}
}

async function loadNotificationsList() {
  try {
    const list = await apiGet("/api/notifications");
    const container = document.getElementById("notif-list");
    if (!container) return;

    if (!list || list.length === 0) {
      container.innerHTML = `<div style="padding:16px; text-align:center; color:var(--dark-muted); font-size:13px;">No notifications yet.</div>`;
      return;
    }

    container.innerHTML = list.map(item => `
      <div class="notif-item ${item.is_read ? '' : 'unread'}">
        <div class="notif-title">${item.title}</div>
        <div>${item.message}</div>
        <div class="notif-time">${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', month: 'short', day: 'numeric'})}</div>
      </div>
    `).join("");
  } catch (e) {
    console.error(e);
  }
}

function handleLogout() {
  clearUserSession();
  showToast("Logged out successfully.", "info");
  setTimeout(() => {
    window.location.href = "/index.html";
  }, 400);
}

document.addEventListener("DOMContentLoaded", () => {
  updateNavigation();
});
