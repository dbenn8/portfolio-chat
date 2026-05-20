// widget/widget.js — Portfolio chat widget
(function() {
  const API_URL = window.PORTFOLIO_CHAT_API || '';
  const GREETING = "Hi! I'm Dan's portfolio assistant. Ask me about any of his projects, his tech stack, or his background.";

  let isOpen = false;
  let messages = [{ role: 'assistant', content: GREETING }];

  function createStyles() {
    const style = document.createElement('style');
    style.textContent = `
      #pc-bubble { position:fixed; bottom:20px; right:20px; width:56px; height:56px; border-radius:50%; background:#10b981; color:white; border:none; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3); z-index:9999; display:flex; align-items:center; justify-content:center; font-size:24px; transition:transform 0.2s; }
      #pc-bubble:hover { transform:scale(1.1); }
      #pc-panel { position:fixed; bottom:88px; right:20px; width:380px; max-height:500px; background:white; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.2); z-index:9999; display:none; flex-direction:column; overflow:hidden; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
      #pc-panel.open { display:flex; }
      #pc-header { background:#0f172a; color:white; padding:14px 16px; font-weight:600; font-size:14px; display:flex; justify-content:space-between; align-items:center; }
      #pc-close { background:none; border:none; color:white; cursor:pointer; font-size:18px; padding:0 4px; }
      #pc-messages { flex:1; overflow-y:auto; padding:12px; max-height:340px; }
      .pc-msg { margin-bottom:10px; line-height:1.5; font-size:13px; }
      .pc-msg.user { text-align:right; }
      .pc-msg.user span { background:#10b981; color:white; padding:8px 12px; border-radius:12px 12px 2px 12px; display:inline-block; max-width:85%; text-align:left; }
      .pc-msg.assistant span { background:#f1f5f9; color:#1e293b; padding:8px 12px; border-radius:12px 12px 12px 2px; display:inline-block; max-width:85%; text-align:left; }
      .pc-msg.assistant span a { color:#10b981; }
      .pc-msg.assistant span strong { font-weight:600; }
      .pc-msg.assistant span code { background:#e2e8f0; padding:1px 4px; border-radius:3px; font-size:12px; }
      #pc-input-row { display:flex; border-top:1px solid #e2e8f0; }
      #pc-input { flex:1; border:none; padding:12px; font-size:13px; outline:none; }
      #pc-send { background:#10b981; color:white; border:none; padding:12px 16px; cursor:pointer; font-weight:600; font-size:13px; }
      #pc-send:hover { background:#059669; }
      #pc-send:disabled { background:#94a3b8; cursor:not-allowed; }
      @media(max-width:440px) { #pc-panel { width:calc(100vw - 24px); right:12px; bottom:80px; } }
    `;
    document.head.appendChild(style);
  }

  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  function createUI() {
    const bubble = document.createElement('button');
    bubble.id = 'pc-bubble';
    bubble.innerHTML = '💬';
    bubble.onclick = toggle;

    const panel = document.createElement('div');
    panel.id = 'pc-panel';
    panel.innerHTML = `
      <div id="pc-header">
        <span>Ask about Dan's projects</span>
        <button id="pc-close" onclick="document.getElementById('pc-panel').classList.remove('open');document.getElementById('pc-bubble').style.display='flex'">✕</button>
      </div>
      <div id="pc-messages"></div>
      <div id="pc-input-row">
        <input id="pc-input" placeholder="Ask me anything..." />
        <button id="pc-send">Send</button>
      </div>
    `;

    document.body.appendChild(bubble);
    document.body.appendChild(panel);

    document.getElementById('pc-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    document.getElementById('pc-send').addEventListener('click', sendMessage);

    renderMessages();
  }

  function toggle() {
    const panel = document.getElementById('pc-panel');
    const bubble = document.getElementById('pc-bubble');
    isOpen = !isOpen;
    panel.classList.toggle('open', isOpen);
    bubble.style.display = isOpen ? 'none' : 'flex';
    if (isOpen) document.getElementById('pc-input').focus();
  }

  function renderMessages() {
    const container = document.getElementById('pc-messages');
    container.innerHTML = messages.map(m =>
      `<div class="pc-msg ${m.role}"><span>${renderMarkdown(m.content)}</span></div>`
    ).join('');
    container.scrollTop = container.scrollHeight;
  }

  async function sendMessage() {
    const input = document.getElementById('pc-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    messages.push({ role: 'user', content: text });
    messages.push({ role: 'assistant', content: '' });
    renderMessages();

    const sendBtn = document.getElementById('pc-send');
    sendBtn.disabled = true;

    try {
      const response = await fetch(API_URL + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            messages[messages.length - 1].content += data;
            renderMessages();
          }
        }
      }
    } catch (err) {
      messages[messages.length - 1].content = 'Sorry, something went wrong. Please try again.';
      renderMessages();
    }

    sendBtn.disabled = false;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { createStyles(); createUI(); });
  } else {
    createStyles(); createUI();
  }
})();
