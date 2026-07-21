document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendButton = document.getElementById('send-button');
    const navChat = document.getElementById('nav-chat');
    const navIntegrations = document.getElementById('nav-integrations');
    const inputWrapper = document.getElementById('input-wrapper');
    const integrationsPanel = document.getElementById('integrations-panel');
    const integrationsGrid = document.getElementById('integrations-grid');

    // Navigation Logic
    navChat.addEventListener('click', () => {
        navChat.classList.add('active');
        navIntegrations.classList.remove('active');
        chatBox.classList.remove('hidden');
        inputWrapper.classList.remove('hidden');
        integrationsPanel.classList.add('hidden');
    });

    navIntegrations.addEventListener('click', async () => {
        navIntegrations.classList.add('active');
        navChat.classList.remove('active');
        chatBox.classList.add('hidden');
        inputWrapper.classList.add('hidden');
        integrationsPanel.classList.remove('hidden');
        
        integrationsGrid.innerHTML = '<p>Loading tools...</p>';
        try {
            const res = await fetch('/api/tools');
            const data = await res.json();
            
            const servers = {};
            data.tools.forEach(t => {
                if (!servers[t.server]) servers[t.server] = [];
                servers[t.server].push(t.name);
            });
            
            integrationsGrid.innerHTML = '';
            for (const [server, tools] of Object.entries(servers)) {
                const card = document.createElement('div');
                card.className = 'integration-card';
                card.innerHTML = `
                    <h3>${server}</h3>
                    <p style="margin-bottom: 12px; font-size: 0.9rem;">
                        <span style="display:inline-block; width:8px; height:8px; background:#10b981; border-radius:50%; margin-right:6px; box-shadow: 0 0 8px #10b981;"></span>
                        Online
                    </p>
                    <p style="font-size: 0.85rem; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px; margin-bottom: 8px;">Available Tools:</p>
                    <ul style="padding-left: 16px; color: #cbd5e1; font-size: 0.85rem; line-height: 1.6;">
                        ${tools.map(t => `<li>${t.replace(/_/g, ' ')}</li>`).join('')}
                    </ul>
                `;
                integrationsGrid.appendChild(card);
            }
        } catch (e) {
            integrationsGrid.innerHTML = `<p style="color:#f5576c;">Failed to load integrations: ${e.message}</p>`;
        }
    });

    // Configure marked to sanitize HTML and render markdown nicely
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function scrollToBottom() {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }

    function addMessage(content, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'AI';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // Parse markdown if it's the AI
        if (sender === 'assistant') {
            bubble.innerHTML = marked.parse(content);
        } else {
            const p = document.createElement('p');
            p.textContent = content;
            bubble.appendChild(p);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function addLoadingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message assistant-message loading-indicator`;
        messageDiv.id = 'current-loading';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = 'AI';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        const typing = document.createElement('div');
        typing.className = 'typing-indicator';
        typing.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        
        bubble.appendChild(typing);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function removeLoadingIndicator() {
        const loading = document.getElementById('current-loading');
        if (loading) {
            loading.remove();
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // UI Updates for User
        addMessage(message, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;
        
        addLoadingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            removeLoadingIndicator();
            
            if (response.ok) {
                addMessage(data.reply, 'assistant');
            } else {
                addMessage(`Error: ${data.detail}`, 'assistant');
            }
            
        } catch (error) {
            removeLoadingIndicator();
            addMessage(`Connection error: ${error.message}`, 'assistant');
        } finally {
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    });
});
