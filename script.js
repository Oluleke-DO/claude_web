// DOM Elements
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesDiv = document.getElementById('messages');
const typingIndicator = document.getElementById('typing-indicator');
const status = document.getElementById('status');

// Initialize the chat
window.addEventListener('load', function() {
    messageInput.focus();
    addWelcomeMessage();
    updateStatus('Ready');
});

// Send message functionality
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    setInputState(false);
    updateStatus('Sending...');
    
    // Display user message
    addMessage(message, 'user-message');
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call your Python API endpoint
        const response = await fetch('/api/claude', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Display Claude's response
        addMessage(data.response, 'ai-message');
        updateStatus('Ready');
        
    } catch (error) {
        console.error('Error calling Claude API:', error);
        hideTypingIndicator();
        addMessage(`Sorry, I encountered an error: ${error.message}`, 'ai-message error');
        updateStatus('Error');
    } finally {
        // Re-enable input
        setInputState(true);
        messageInput.focus();
    }
}

function addMessage(content, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    
    // Format the content (handle code blocks, etc.)
    if (className.includes('ai-message')) {
        messageDiv.innerHTML = formatMessage(content);
    } else {
        messageDiv.textContent = content;
    }
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessage(content) {
    // Check if content exists and is a string
    if (!content || typeof content !== 'string') {
        return 'No response received :'+ content;
    }
    
    // Basic formatting for code blocks and markdown-like content
    return content
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    updateStatus('Claude is typing...');
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function setInputState(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    sendBtn.textContent = enabled ? 'Send' : 'Sending...';
}

function updateStatus(text) {
    status.textContent = text;
}

function scrollToBottom() {
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addWelcomeMessage() {
    addMessage('Hello! I\'m Claude. How can I help you today?', 'ai-message');
}

// Auto-resize input on mobile
if (window.innerWidth <= 768) {
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}