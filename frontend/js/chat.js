/**
 * Khane ki Khoj - Tiffin Services
 * Direct Chat Script: Conversations List, Live Polling, Message Sending
 */

/**
 * Format a UTC timestamp string to Asia/Kolkata (IST) local time.
 * Handles naive ISO strings (no Z suffix) by treating them as UTC.
 * Shows time only for today's messages; prepends short date for older messages.
 */
function formatChatTimestamp(dateInput) {
  if (!dateInput) return '';
  let str = typeof dateInput === 'string' ? dateInput.trim() : String(dateInput);
  // If no timezone info present, treat as UTC by appending Z
  if (!str.endsWith('Z') && !/[+-]\d{2}(:?\d{2})?$/.test(str)) {
    str += 'Z';
  }
  const date = new Date(str);
  if (isNaN(date.getTime())) return '';
  const timeFormatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit', minute: '2-digit', hour12: true
  });
  const toDateKey = (d) => new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit'
  }).format(d);
  const now = new Date();
  if (toDateKey(date) !== toDateKey(now)) {
    const shortDate = new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Kolkata', month: 'short', day: 'numeric'
    }).format(date);
    return shortDate + ', ' + timeFormatter.format(date);
  }
  return timeFormatter.format(date);
}

let activeConversationId = null;
let chatPollingTimer = null;
let currentUser = null;
let lastRenderedCount = -1;
let lastRenderedLastId = null;

document.addEventListener("DOMContentLoaded", () => {
  currentUser = getUser();
  if (!currentUser) {
    showToast("Please log in to access the direct chat feature.", "info");
    setTimeout(() => window.location.href = "/login.html", 500);
    return;
  }

  // Check URL param for requested conversation
  const urlParams = new URLSearchParams(window.location.search);
  const requestedConvId = urlParams.get("conv");

  loadConversations(requestedConvId);

  // Setup message send form
  const messageForm = document.getElementById("chat-message-form");
  if (messageForm) {
    messageForm.addEventListener("submit", handleSendMessage);
  }
});

// ================= Load All Conversations =================
async function loadConversations(autoSelectId = null) {
  const listContainer = document.getElementById("conversations-list");
  if (!listContainer) return;

  try {
    const conversations = await apiGet("/api/conversations");

    if (!conversations || conversations.length === 0) {
      listContainer.innerHTML = `
        <div style="padding:24px; text-align:center; color:var(--dark-muted); font-size:13px;">
          No conversations yet.<br><br>
          ${currentUser.role === 'student' ? '<a href="/student-dashboard.html" class="btn btn-primary btn-sm">Find Tiffin to Chat</a>' : 'When students message your tiffin service, they will appear here.'}
        </div>
      `;
      return;
    }

    listContainer.innerHTML = conversations.map(c => {
      const otherPartyName = currentUser.role === "student" ? c.provider_name : c.student_name;
      const initial = otherPartyName.charAt(0).toUpperCase();
      const isActive = activeConversationId === c.id || (autoSelectId && String(autoSelectId) === String(c.id));

      return `
        <div class="chat-conv-item ${isActive ? 'active' : ''}" onclick="selectConversation(${c.id}, '${otherPartyName.replace(/'/g, "\\'")}')">
          <div class="chat-conv-avatar">${initial}</div>
          <div class="chat-conv-info">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div class="chat-conv-name">${otherPartyName}</div>
              ${c.unread_count > 0 ? `<span class="badge" style="background:var(--danger); color:#fff; font-size:10px;">${c.unread_count}</span>` : ''}
            </div>
            <div class="chat-conv-last-msg">${c.last_message || 'Start chatting...'}</div>
          </div>
        </div>
      `;
    }).join("");

    // Auto-select conversation
    if (autoSelectId) {
      const target = conversations.find(c => String(c.id) === String(autoSelectId));
      if (target) {
        const name = currentUser.role === "student" ? target.provider_name : target.student_name;
        selectConversation(target.id, name);
      }
    } else if (conversations.length > 0 && !activeConversationId) {
      const first = conversations[0];
      const name = currentUser.role === "student" ? first.provider_name : first.student_name;
      selectConversation(first.id, name);
    }
  } catch (err) {
    console.error("Failed to load conversations:", err);
  }
}

// ================= Select Active Conversation =================
window.selectConversation = function(convId, otherPartyName) {
  if (activeConversationId !== convId) {
    activeConversationId = convId;
    lastRenderedCount = -1;
    lastRenderedLastId = null;
  }

  // Highlight active conversation in sidebar
  document.querySelectorAll(".chat-conv-item").forEach(el => el.classList.remove("active"));
  // (Sidebar re-renders on refresh anyway)

  // Update Header
  const nameEl = document.getElementById("chat-active-name");
  const roleEl = document.getElementById("chat-active-role");
  if (nameEl) nameEl.innerText = otherPartyName;
  if (roleEl) roleEl.innerText = currentUser.role === "student" ? "Verified Tiffin Provider" : "Student Customer";

  // Enable input field
  const input = document.getElementById("chat-message-input");
  const sendBtn = document.getElementById("chat-send-btn");
  if (input) {
    input.disabled = false;
    input.placeholder = `Message ${otherPartyName}...`;
    input.focus();
  }
  if (sendBtn) sendBtn.disabled = false;

  // Load message history (initial load: isPolling = false -> auto-scrolls to bottom)
  loadMessages(convId, false);

  // Restart polling timer for this conversation (every 3 seconds)
  if (chatPollingTimer) clearInterval(chatPollingTimer);
  chatPollingTimer = setInterval(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId, true);
    }
  }, 3000);
};

// ================= Load Messages for Conversation =================
async function loadMessages(convId, isPolling = false) {
  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  // Detect scroll state before replacing messages:
  // User is considered near bottom if within 100px of the bottom
  const prevScrollTop = container.scrollTop;
  const isNearBottom = (container.scrollHeight - container.scrollTop - container.clientHeight) < 100;

  try {
    const messages = await apiGet(`/api/conversations/${convId}/messages`);

    if (!messages || messages.length === 0) {
      lastRenderedCount = 0;
      lastRenderedLastId = null;
      container.innerHTML = `
        <div style="text-align:center; padding:40px; color:var(--dark-muted); font-size:13px;">
          💬 No messages yet. Say hello and introduce yourself!
        </div>
      `;
      return;
    }

    const newLastId = messages[messages.length - 1]?.id;
    const hasChanged = messages.length !== lastRenderedCount || newLastId !== lastRenderedLastId;

    // During polling, if no new messages arrived, leave the DOM untouched to avoid any scroll disruption
    if (isPolling && !hasChanged) {
      return;
    }

    lastRenderedCount = messages.length;
    lastRenderedLastId = newLastId;

    container.innerHTML = messages.map(m => {
      const isSentByMe = m.sender_id === currentUser.user_id;
      const bubbleClass = isSentByMe ? "message-sent" : "message-received";
      const timeStr = formatChatTimestamp(m.created_at);

      return `
        <div class="message-bubble ${bubbleClass}">
          <div>${m.message_text}</div>
          <div class="message-time">${timeStr}</div>
        </div>
      `;
    }).join("");

    // Auto-scroll logic:
    // Scroll to bottom if:
    // 1. Initial conversation open or user just sent a message (!isPolling)
    // 2. OR user was already near the bottom when new message arrived (isNearBottom)
    // Otherwise, keep user's current reading position so polling does not disrupt them.
    if (!isPolling || isNearBottom) {
      container.scrollTop = container.scrollHeight;
    } else {
      container.scrollTop = prevScrollTop;
    }
  } catch (err) {
    console.error("Failed to load messages:", err);
  }
}

// ================= Send Message =================
async function handleSendMessage(e) {
  e.preventDefault();
  if (!activeConversationId) return;

  const input = document.getElementById("chat-message-input");
  const sendBtn = document.getElementById("chat-send-btn");
  const text = input.value.trim();

  if (!text) return;

  try {
    input.value = "";
    sendBtn.disabled = true;

    await apiPost(`/api/conversations/${activeConversationId}/messages`, {
      message_text: text
    });

    // Refresh messages immediately
    await loadMessages(activeConversationId, false);
    loadConversations(); // Update last message in sidebar
  } catch (err) {
    showToast(err.message || "Failed to send message.", "error");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}
