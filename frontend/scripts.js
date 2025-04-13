// Theme handling
const ThemeManager = {
    init() {
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        const savedTheme = localStorage.getItem('theme');
        const theme = savedTheme || (prefersDark.matches ? 'dark' : 'light');
        this.setTheme(theme);
        
        themeToggle?.addEventListener('click', () => {
            const newTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        });
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
};

// Chat functionality
const ChatManager = {
    API_URL: 'http://localhost:8000',
    elements: {},
    isProcessing: false,

    init() {
        this.elements = {
            messages: document.getElementById('messages'),
            userInput: document.getElementById('user-input'),
            sendButton: document.getElementById('send-button'),
            charCount: document.getElementById('char-count')
        };

        if (!this.validateElements()) {
            console.error('Failed to initialize chat: Missing required elements');
            return;
        }

        this.addMessage('Hello! How can I assist you with your health concerns today?', false);
        this.setupEventListeners();
        this.updateInput();
        this.elements.userInput.focus();
    },

    validateElements() {
        return Object.values(this.elements).every(element => element !== null);
    },

    updateInput() {
        const { userInput, charCount, sendButton } = this.elements;
        const text = userInput.value.trim();
        
        charCount.textContent = `${text.length}/500`;
        sendButton.disabled = !text || this.isProcessing;
        
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    },

    addMessage(text, isUser) {
        const { messages } = this.elements;
        const message = document.createElement('div');
        message.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = isUser ? '👤' : '👨‍⚕️';
        
        if (isUser) {
            message.appendChild(bubble);
            message.appendChild(avatar);
        } else {
            message.appendChild(avatar);
            message.appendChild(bubble);
        }
        
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        return message;
    },

    createTypingIndicator() {
        const message = document.createElement('div');
        message.className = 'message bot typing';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '👨‍⚕️';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble typing-indicator';
        
        const dots = document.createElement('div');
        dots.className = 'dots';
        for (let i = 0; i < 3; i++) {
            dots.appendChild(document.createElement('span')).className = 'dot';
        }
        
        bubble.appendChild(dots);
        message.appendChild(avatar);
        message.appendChild(bubble);
        return message;
    },

    async sendMessage() {
        const { userInput } = this.elements;
        const text = userInput.value.trim();
        
        if (!text || this.isProcessing) return;
        
        this.isProcessing = true;
        let typingMsg = null;
        
        try {
            this.addMessage(text, true);
            userInput.value = '';
            this.updateInput();
            
            typingMsg = this.createTypingIndicator();
            this.elements.messages.appendChild(typingMsg);
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            
            const response = await fetch(`${this.API_URL}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Server error');
            }
            
            if (!data.answer) {
                throw new Error('Invalid response format');
            }
            
            this.addMessage(data.answer, false);
        } catch (error) {
            console.error('Chat Error:', error);
            this.addMessage('Sorry, there was an error processing your request. Please try again.', false);
        } finally {
            typingMsg?.remove();
            this.isProcessing = false;
            this.updateInput();
            userInput.focus();
        }
    },

    setupEventListeners() {
        const { userInput, sendButton } = this.elements;
        
        userInput.addEventListener('input', () => this.updateInput());
        sendButton.addEventListener('click', () => this.sendMessage());
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
};

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    ChatManager.init();
});
