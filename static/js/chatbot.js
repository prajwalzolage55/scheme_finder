// ── Chatbot Logic ─────────────────────────────────────────────────────────────
const messagesDiv  = document.getElementById('chat-messages');
const inputEl      = document.getElementById('chat-input');
const sendBtn      = document.getElementById('send-btn');
const suggestions  = document.getElementById('suggestions');

let conversationHistory = [];
let isTyping = false;

// ── Helpers ───────────────────────────────────────────────────────────────────
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function scrollToBottom() {
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function timeNow() {
  return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

// ── Append Messages ───────────────────────────────────────────────────────────
function appendUserMessage(text) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;flex-direction:column;align-items:flex-end;gap:4px';
  wrapper.innerHTML = `
    <div class="msg-bubble msg-user">${escapeHtml(text)}</div>
    <div style="font-size:0.72rem;color:var(--gray-md);padding-right:4px">You · ${timeNow()}</div>
  `;
  messagesDiv.appendChild(wrapper);
  scrollToBottom();
}

function appendBotMessage(html) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;gap:10px;align-items:flex-start';
  wrapper.innerHTML = `
    <div style="width:36px;height:36px;background:linear-gradient(135deg,var(--saffron),#FF3B00);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">🤖</div>
    <div>
      <div class="msg-bubble msg-bot">${html}</div>
      <div style="font-size:0.72rem;color:var(--gray-md);margin-top:4px;padding-left:4px">SchemeSaathi AI · ${timeNow()}</div>
    </div>
  `;
  messagesDiv.appendChild(wrapper);
  scrollToBottom();
}

function showTyping() {
  const wrapper = document.createElement('div');
  wrapper.id = 'typing-wrapper';
  wrapper.style.cssText = 'display:flex;gap:10px;align-items:flex-start';
  wrapper.innerHTML = `
    <div style="width:36px;height:36px;background:linear-gradient(135deg,var(--saffron),#FF3B00);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">🤖</div>
    <div class="msg-bubble msg-bot">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  messagesDiv.appendChild(wrapper);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typing-wrapper');
  if (el) el.remove();
}

// ── Send Message ──────────────────────────────────────────────────────────────
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || isTyping) return;

  // Hide suggestions after first message
  if (suggestions) suggestions.style.display = 'none';

  isTyping = true;
  sendBtn.disabled = true;
  inputEl.value = '';
  inputEl.style.height = 'auto';

  appendUserMessage(text);

  conversationHistory.push({ role: 'user', content: text });

  showTyping();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: conversationHistory })
    });

    const data = await response.json();
    removeTyping();

    if (data.reply) {
      const formatted = escapeHtml(data.reply);
      appendBotMessage(formatted);
      conversationHistory.push({ role: 'assistant', content: data.reply });
    } else if (data.error) {
      appendBotMessage(`⚠️ ${data.error}`);
    }
  } catch (err) {
    removeTyping();
    appendBotMessage('⚠️ Connection error. Please check your internet and try again.');
    console.error('Chat error:', err);
  }

  isTyping = false;
  sendBtn.disabled = false;
  inputEl.focus();
}

// ── Keyboard Handler ──────────────────────────────────────────────────────────
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ── Suggestion Chips ──────────────────────────────────────────────────────────
function useSuggestion(btn) {
  inputEl.value = btn.textContent;
  autoResize(inputEl);
  inputEl.focus();
  sendMessage();
}
