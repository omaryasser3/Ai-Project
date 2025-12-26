document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const codeInput = document.getElementById('code-input');
    const sendBtn = document.getElementById('send-btn');
    const langSelect = document.getElementById('lang-select');
    const template = document.getElementById('message-template');

    // Auto-resize textarea
    codeInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() === '') {
            this.style.height = 'auto';
        }
    });

    // Handle Send
    sendBtn.addEventListener('click', handleSend);
    codeInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    let lastCode = '';
    let lastLang = '';

    async function handleSend() {
        const code = codeInput.value.trim();
        const lang = langSelect.value;

        if (!code) return;

        // Update state for regenerate
        lastCode = code;
        lastLang = lang;

        // Add User Message
        addMessage(code, 'user');
        codeInput.value = '';
        codeInput.style.height = 'auto';

        // Show Thinking
        const thinkingId = addThinking();

        try {
            // Call API
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: code,
                    src_lang: lang,
                    bug_id: "web_session_" + Date.now()
                })
            });

            const data = await response.json();

            // Remove Thinking
            removeMessage(thinkingId);

            if (response.ok) {
                // Show Agent Response
                const explanation = data.explanation || "I've fixed existing issues.";
                const fixedCode = data.fixed_code;

                const markdownContent = `
**Explanation:**
${explanation}

**Fixed Code:**
\`\`\`${lang.toLowerCase()}
${fixedCode}
\`\`\`
`;
                const msgId = addMessage(markdownContent, 'agent', true);
            } else {
                addMessage(`Error: ${data.detail || 'Something went wrong.'}`, 'agent');
            }

        } catch (error) {
            removeMessage(thinkingId);
            addMessage(`Error: ${error.message}`, 'agent');
        }
    }

    function addMessage(text, flow, withActions = false) {
        const clone = template.content.cloneNode(true);
        const msgEl = clone.querySelector('.message');
        const contentEl = clone.querySelector('.message-text');
        const actionsEl = clone.querySelector('.message-actions');

        msgEl.classList.add(flow);

        // Render Markdown if agent, else regular text
        if (flow === 'agent') {
            contentEl.innerHTML = marked.parse(text);
        } else {
            contentEl.textContent = text; // User code typically just pre-wrap
            // Or wrap user code in block
            contentEl.innerHTML = `<pre><code>${escapeHtml(text)}</code></pre>`;
        }

        chatContainer.appendChild(clone);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const insertedMsg = chatContainer.lastElementChild;

        if (withActions) {
            actionsEl.classList.remove('hidden');

            const acceptBtn = actionsEl.querySelector('.accept-btn');
            const regenerateBtn = actionsEl.querySelector('.regenerate-btn');
            const stopBtn = actionsEl.querySelector('.stop-btn');

            acceptBtn.onclick = () => {
                actionsEl.classList.add('hidden');
                addMessage("✅ Solution Accepted!", 'user');
                addMessage("Great! Let me know if you have any other code to fix.", 'agent');
            };

            stopBtn.onclick = () => {
                actionsEl.classList.add('hidden');
                addMessage("⛔ flow stopped.", 'user');
            };

            regenerateBtn.onclick = () => {
                actionsEl.classList.add('hidden');
                addMessage("🔄 Regenerate, please.", 'user');
                // Trigger regenerate logic - effectively sending the same code again
                // In a real app we might pass context, but here we just re-run for simplicity/demo
                // We need the original code. For now, we rely on the user re-pasting or we store it?
                // Better UX: Store the last code in a variable.
                if (lastCode) {
                    // Re-trigger send logic manually
                    // To keep it simple, we just call the API again directly
                    retrySolve(lastCode, lastLang);
                }
            };
        }

        return insertedMsg;
    }

    // Duplicate logic for retry to avoid circular dependency cleaning
    async function retrySolve(code, lang) {
        const thinkingId = addThinking();
        try {
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: code,
                    src_lang: lang,
                    bug_id: "web_session_retry_" + Date.now()
                })
            });

            const data = await response.json();
            removeMessage(thinkingId);

            if (response.ok) {
                const explanation = data.explanation || "Here is another attempt.";
                const fixedCode = data.fixed_code;
                const markdownContent = `**Regenerated Solution:**\n\n${explanation}\n\n\`\`\`${lang.toLowerCase()}\n${fixedCode}\n\`\`\``;
                addMessage(markdownContent, 'agent', true);
            } else {
                addMessage(`Error: ${data.detail}`, 'agent');
            }
        } catch (e) {
            removeMessage(thinkingId);
            addMessage(`Error: ${e.message}`, 'agent');
        }
    }

    function addThinking() {
        const id = 'thinking-' + Date.now();
        const html = `<div id="${id}" class="message agent">
            <div class="message-avatar"></div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>`;
        chatContainer.insertAdjacentHTML('beforeend', html);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
