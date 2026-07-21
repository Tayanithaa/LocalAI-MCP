document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendButton = document.getElementById('send-button');

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
