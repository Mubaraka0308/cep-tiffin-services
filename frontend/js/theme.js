/**
 * Khane Ki Khoj - Theme Management System
 * Supports Light & Dark Modes with LocalStorage and System Preference
 * Prevents FOUC (Flash of Unstyled Content) by executing synchronously
 */

(function () {
  const savedTheme = localStorage.getItem("theme");
  let theme = "light";
  if (savedTheme === "dark" || savedTheme === "light") {
    theme = savedTheme;
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    theme = "dark";
  }
  document.documentElement.setAttribute("data-theme", theme);
})();

function getTheme() {
  return document.documentElement.getAttribute("data-theme") || "light";
}

function toggleTheme() {
  const current = getTheme();
  const next = current === "dark" ? "light" : "dark";
  setTheme(next);
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  updateThemeToggleUI();
}

function getSunIcon() {
  return `<svg class="theme-icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
  </svg>`;
}

function getMoonIcon() {
  return `<svg class="theme-icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  </svg>`;
}

function updateThemeToggleUI() {
  const isDark = getTheme() === "dark";
  const label = isDark ? "Switch to light mode" : "Switch to dark mode";
  const iconHtml = isDark ? getSunIcon() : getMoonIcon();

  const btns = document.querySelectorAll(".theme-toggle-btn");
  btns.forEach(btn => {
    btn.setAttribute("aria-label", label);
    btn.setAttribute("title", label);
    btn.innerHTML = iconHtml;
  });
}

function setupThemeToggle() {
  updateThemeToggleUI();
  const btns = document.querySelectorAll(".theme-toggle-btn");
  btns.forEach(btn => {
    if (!btn.dataset.themeBound) {
      btn.dataset.themeBound = "true";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        toggleTheme();
      });
    }
  });
}

// Listen for system color scheme changes if user hasn't explicitly set a preference
if (window.matchMedia) {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
      setTheme(e.matches ? "dark" : "light");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupThemeToggle();
});

// Expose globally
window.toggleTheme = toggleTheme;
window.setTheme = setTheme;
window.getTheme = getTheme;
window.setupThemeToggle = setupThemeToggle;
window.updateThemeToggleUI = updateThemeToggleUI;
window.getSunIcon = getSunIcon;
window.getMoonIcon = getMoonIcon;
