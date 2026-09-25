/**
 * Khane ki Khoj - Tiffin Services
 * Direct Chat Script: Conversations List, Live Polling, Message Sending
 */

let activeConversationId = null;
let chatPollingTimer = null;
let currentUser = null;

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
  activeConversationId = convId;

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

  // Load message history
  loadMessages(convId);

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

  try {
    const messages = await apiGet(`/api/conversations/${convId}/messages`);

    if (!messages || messages.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:40px; color:var(--dark-muted); font-size:13px;">
          💬 No messages yet. Say hello and introduce yourself!
        </div>
      `;
      return;
    }

    container.innerHTML = messages.map(m => {
      const isSentByMe = m.sender_id === currentUser.user_id;
      const bubbleClass = isSentByMe ? "message-sent" : "message-received";
      const timeStr = new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      return `
        <div class="message-bubble ${bubbleClass}">
          <div>${m.message_text}</div>
          <div class="message-time">${timeStr}</div>
        </div>
      `;
    }).join("");

    // Auto-scroll to bottom only if not manually scrolled or on initial load
    if (!isPolling) {
      container.scrollTop = container.scrollHeight;
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
