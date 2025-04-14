const API_URL = 'http://localhost:8000';
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user' : 'bot');
    
    // Add typing effect for bot messages
    if (!isUser) {
        let i = 0;
        const typing = setInterval(() => {
            messageDiv.textContent = text.slice(0, i);
            i++;
            chatMessages.scrollTop = chatMessages.scrollHeight;
            if (i > text.length) {
                clearInterval(typing);
            }
        }, 20);
    } else {
        messageDiv.textContent = text;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading');
    loadingDiv.id = 'loadingMessage';
    loadingDiv.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Cura is thinking...';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoading() {
    const loadingDiv = document.getElementById('loadingMessage');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

async function sendMessage(message) {
    try {
        showLoading();
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        removeLoading();
        addMessage(data.answer, false);
    } catch (error) {
        removeLoading();
        const errorDiv = document.createElement('div');
        errorDiv.classList.add('error');
        errorDiv.textContent = 'Sorry, there was an error processing your request.';
        chatMessages.appendChild(errorDiv);
    }
}

function handleSend() {
    const message = messageInput.value.trim();
    if (message) {
        addMessage(message, true);
        messageInput.value = '';
        sendMessage(message);
    }
}

sendButton.addEventListener('click', handleSend);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});

// Add welcome message
addMessage('Hello! I\'m Cura, your medical assistant. How can I help you today?', false);