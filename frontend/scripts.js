const API_URL = 'http://localhost:8000';
const MAX_MESSAGE_LENGTH = 500;
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const clearButton = document.getElementById('clearButton');
let conversationId = Date.now().toString();

function createMessageElement(content, isUser) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isUser ? 'user-wrapper' : 'bot-wrapper'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    if (!isUser) {
        message.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        setTimeout(() => {
            typeMessage(message, content);
        }, 500);
    } else {
        message.textContent = content;
    }
    
    messageContent.appendChild(message);
    messageContent.appendChild(timestamp);
    wrapper.append(isUser ? messageContent : avatar, isUser ? avatar : messageContent);
    
    return wrapper;
}

function typeMessage(element, text) {
    let index = 0;
    element.textContent = '';
    
    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, Math.random() * 30 + 20);
        }
    }
    type();
}

function addMessage(content, isUser = false) {
    const messageElement = createMessageElement(content, isUser);
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addThinkingIndicator() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-wrapper thinking-wrapper';
    wrapper.id = 'thinkingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const message = document.createElement('div');
    message.className = 'message bot thinking';
    message.innerHTML = `
        <div class="thinking-content">
            <span class="thinking-text">Cura is thinking</span>
            <div class="thinking-dots"><span></span><span></span><span></span></div>
        </div>
    `;
    
    messageContent.appendChild(message);
    wrapper.append(avatar, messageContent);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeThinkingIndicator() {
    const indicator = document.getElementById('thinkingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessage(message) {
    messageInput.value = '';
    updateCharCounter();
    messageInput.disabled = true;
    sendButton.disabled = true;
    
    addThinkingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                question: message,
                conversationId: conversationId
            })
        });

        if (!response.ok) throw new Error('Network response was not ok');
        
        removeThinkingIndicator();
        const data = await response.json();
        addMessage(data.answer, false);
    } catch (error) {
        removeThinkingIndicator();
        showError('Sorry, there was an error processing your request.');
        console.error('Error:', error);
    } finally {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message-wrapper error-wrapper';
    errorDiv.innerHTML = `
        <div class="message error">
            <i class="fas fa-exclamation-circle"></i>
            ${message}
        </div>
    `;
    chatMessages.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function updateCharCounter() {
    const length = messageInput.value.length;
    const counter = document.getElementById('charCounter');
    counter.textContent = `${length}/${MAX_MESSAGE_LENGTH}`;
    counter.style.color = length > MAX_MESSAGE_LENGTH ? '#dc2626' : '#64748b';
    sendButton.disabled = length > MAX_MESSAGE_LENGTH;
}

function handleSend() {
    const message = messageInput.value.trim();
    if (message && message.length <= MAX_MESSAGE_LENGTH) {
        addMessage(message, true);
        sendMessage(message);
    }
}

async function clearHistory() {
    try {
        await fetch(`${API_URL}/history/${conversationId}`, { method: 'DELETE' });
        chatMessages.innerHTML = '';
        conversationId = Date.now().toString();
        addMessage("Hello! I'm Cura, your medical assistant. How can I help you today?", false);
    } catch (error) {
        showError('Failed to clear chat history.');
    }
}

messageInput.addEventListener('input', updateCharCounter);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});
sendButton.addEventListener('click', handleSend);
clearButton.addEventListener('click', clearHistory);

// Initialize chat
addMessage("Hello! I'm Cura, your medical assistant. How can I help you today?", false);