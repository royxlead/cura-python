/**
 * Cura AI - Simple Medical Assistant Application
 * Simplified version without authentication
 */

// Simple Application State
class AppState {
    constructor() {
        this.currentView = 'welcome';
        this.chatMessages = [];
        this.settings = {
            theme: 'light'
        };
    }

    setState(key, value) {
        this[key] = value;
    }
}

// API Service
class APIService {
    constructor() {
        // Use backend server URL
        this.baseURL = 'http://localhost:8000';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        console.log('Making API request to:', url); // Debug log
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            console.error('Failed URL:', url); // Debug log
            throw error;
        }
    }

    async sendMessage(message) {
        const response = await this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
        return response;
    }
}

// Chat Manager
class ChatManager {
    constructor(apiService, notifications) {
        this.api = apiService;
        this.notifications = notifications;
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendBtn'); // Fixed ID
        this.isTyping = false;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        console.log('Setting up chat event listeners...');
        console.log('Send button found:', this.sendButton);
        console.log('Message input found:', this.messageInput);
        
        // Send button
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => {
                console.log('Send button clicked!');
                this.handleSendMessage();
            });
        }

        // Message input
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('Enter key pressed!');
                    this.handleSendMessage();
                }
            });

            this.messageInput.addEventListener('input', () => {
                this.updateSendButton();
                this.updateCharCount();
            });
        }
        
        // Category buttons at bottom
        const symptomsBtn = document.querySelector('[data-action="symptoms"]');
        const medicationBtn = document.querySelector('[data-action="medication"]');
        const emergencyBtn = document.querySelector('[data-action="emergency"]');
        
        console.log('Category buttons found:', { symptomsBtn, medicationBtn, emergencyBtn });
        
        if (symptomsBtn) {
            symptomsBtn.addEventListener('click', () => {
                console.log('Symptoms category clicked!');
                this.handleCategoryClick('symptoms');
            });
        }
        
        if (medicationBtn) {
            medicationBtn.addEventListener('click', () => {
                console.log('Medication category clicked!');
                this.handleCategoryClick('medication');
            });
        }
        
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => {
                console.log('Emergency category clicked!');
                this.handleCategoryClick('emergency');
            });
        }
    }
    
    handleCategoryClick(category) {
        const prompts = {
            symptoms: "I'd like to discuss my symptoms. ",
            medication: "I have a question about medication. ",
            emergency: "This is an urgent medical question. "
        };
        
        if (this.messageInput) {
            this.messageInput.value = prompts[category];
            this.messageInput.focus();
            this.updateSendButton();
        }
    }
    
    sendPredefinedMessage(message) {
        if (this.messageInput) {
            this.messageInput.value = message;
            this.updateSendButton();
            // Automatically send the message
            setTimeout(() => {
                this.handleSendMessage();
            }, 100);
        }
    }

    updateSendButton() {
        const hasText = this.messageInput?.value.trim().length > 0;
        console.log('Updating send button - hasText:', hasText, 'input value:', this.messageInput?.value);
        if (this.sendButton) {
            this.sendButton.disabled = !hasText;
            this.sendButton.classList.toggle('active', hasText);
            console.log('Send button disabled:', this.sendButton.disabled);
        }
    }
    
    updateCharCount() {
        const charCountElement = document.getElementById('charCount');
        if (charCountElement && this.messageInput) {
            const currentLength = this.messageInput.value.length;
            charCountElement.textContent = currentLength;
            
            // Change color if approaching limit
            const inputContainer = this.messageInput.closest('.input-container');
            if (inputContainer) {
                inputContainer.classList.toggle('near-limit', currentLength > 1800);
            }
        }
    }

    async handleSendMessage() {
        const message = this.messageInput?.value.trim();
        if (!message) return;

        // Clear input
        this.messageInput.value = '';
        this.updateSendButton();

        // Add user message
        this.addMessage(message, 'user');

        try {
            // Show typing indicator
            this.showTypingIndicator();

            // Send to API
            const response = await this.api.sendMessage(message);

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add AI response
            this.addMessage(response.message, 'assistant');

        } catch (error) {
            this.hideTypingIndicator();
            this.notifications.error('Failed to send message. Please try again.');
            console.error('Send message error:', error);
        }
    }

    addMessage(content, role, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const timestamp = new Date().toLocaleTimeString();
        
        // Format content for better readability
        let formattedContent = content;
        if (role === 'assistant' && typeof content === 'string') {
            formattedContent = this.formatAIResponse(content);
        }

        messageDiv.innerHTML = `
            <div class="message-avatar ${role}-avatar">
                <span class="material-symbols-rounded">
                    ${role === 'user' ? 'person' : 'health_and_safety'}
                </span>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">${role === 'user' ? 'You' : 'Cura AI'}</span>
                    <span class="message-time">${timestamp}</span>
                </div>
                <div class="message-text">${formattedContent}</div>
            </div>
        `;

        this.messagesContainer?.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatAIResponse(content) {
        // Don't format if it's already HTML (like welcome message)
        if (content.includes('<div class="welcome-content">')) {
            return content;
        }

        // Split content into paragraphs and format
        let formatted = content
            // Split by double newlines for paragraphs
            .split('\n\n')
            .map(paragraph => {
                // Handle bullet points
                if (paragraph.includes('* **')) {
                    const items = paragraph
                        .split('* **')
                        .filter(item => item.trim())
                        .map(item => {
                            // Fix the colon issue - look for patterns like "Title:** description"
                            if (item.includes(':**')) {
                                const [title, ...rest] = item.split(':**');
                                return `<li><strong>${title}:</strong>${rest.join(':**')}</li>`;
                            } else if (item.includes('**')) {
                                // Handle cases where ** appears but isn't properly closed
                                const cleanItem = item.replace(/\*\*/g, '');
                                return `<li><strong>${cleanItem}</strong></li>`;
                            }
                            return `<li>${item}</li>`;
                        });
                    return `<ul class="ai-response-list">${items.join('')}</ul>`;
                }
                
                // Handle single bullet points
                if (paragraph.includes('* ')) {
                    const items = paragraph
                        .split('* ')
                        .filter(item => item.trim())
                        .map(item => {
                            // First fix malformed bold patterns like **Text:** or **Text:*
                            let cleanItem = item
                                .replace(/\*\*(.*?):\*+/g, '<strong>$1:</strong>') // **Text:** or **Text:*
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');  // **Text**
                            return `<li>${cleanItem}</li>`;
                        });
                    return `<ul class="ai-response-list">${items.join('')}</ul>`;
                }
                
                // Handle regular paragraphs
                if (paragraph.trim()) {
                    let formatted = paragraph
                        // Fix malformed patterns first
                        .replace(/\*\*(.*?):\*+/g, '<strong>$1:</strong>') // **Text:** or **Text:*
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // **Text**
                        .replace(/\*(.*?)\*/g, '<em>$1</em>');             // *text*
                    
                    return `<p>${formatted}</p>`;
                }
                
                return '';
            })
            .join('');

        return `<div class="ai-response-formatted">${formatted}</div>`;
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-message';
        typingDiv.id = 'typingIndicator';

        typingDiv.innerHTML = `
            <div class="message-avatar ai-avatar">
                <span class="material-symbols-rounded">health_and_safety</span>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        this.messagesContainer?.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
}

// Notification System
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', options = {}) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icon = this.getIcon(type);
        notification.innerHTML = `
            <div class="notification-icon">
                <span class="material-symbols-rounded">${icon}</span>
            </div>
            <div class="notification-content">
                ${options.title ? `<div class="notification-title">${options.title}</div>` : ''}
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">
                <span class="material-symbols-rounded">close</span>
            </button>
        `;

        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => this.remove(notification));

        this.container.appendChild(notification);

        // Auto remove after duration
        const duration = options.duration || 5000;
        setTimeout(() => this.remove(notification), duration);

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        return icons[type] || 'info';
    }

    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    remove(notification) {
        if (notification && notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }
}

// Main Application Class
class CuraApp {
    constructor() {
        this.state = new AppState();
        this.api = new APIService();
        this.notifications = new NotificationSystem();
        this.chatManager = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupThemeToggle();
        this.showView('welcome');
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Get Started button
        const getStartedBtn = document.getElementById('getStartedBtn');
        console.log('Get Started button found:', getStartedBtn);
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', () => {
                console.log('Get Started button clicked!');
                this.startChat();
            });
        }

        // Learn More button
        const learnMoreBtn = document.getElementById('learnMoreBtn');
        console.log('Learn More button found:', learnMoreBtn);
        if (learnMoreBtn) {
            learnMoreBtn.addEventListener('click', () => {
                console.log('Learn More button clicked!');
                this.showLearnMore();
            });
        }
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    startChat() {
        this.showChatInterface();
    }

    showChatInterface() {
        // Hide welcome section
        const welcomeSection = document.getElementById('authSection');
        if (welcomeSection) {
            welcomeSection.style.display = 'none';
        }

        // Show chat section
        const chatSection = document.getElementById('chatSection');
        if (chatSection) {
            chatSection.classList.remove('hidden');
            chatSection.style.display = 'flex';
        }

        // Initialize chat manager if not already done
        if (!this.chatManager) {
            this.chatManager = new ChatManager(this.api, this.notifications);
            
            // Add welcome message
            setTimeout(() => {
                const welcomeMessage = `
                    <div class="welcome-content">
                        <h3>👋 Hello! I'm Cura, your AI medical assistant.</h3>
                        <p>I'm here to help you with your health questions and concerns. I can assist you with:</p>
                        <ul class="feature-list">
                            <li>🔍 <strong>Symptom Analysis</strong> - Analyze your symptoms and provide differential diagnosis</li>
                            <li>💊 <strong>Medication Information</strong> - Details about drugs, interactions, and side effects</li>
                            <li>🏥 <strong>Health Guidance</strong> - General medical advice and health tips</li>
                            <li>🚨 <strong>Emergency Support</strong> - Immediate guidance for urgent situations</li>
                        </ul>
                        <p><strong>How can I help you today?</strong></p>
                    </div>
                `;
                this.chatManager.addMessage(welcomeMessage, 'assistant');
            }, 500);
        } else {
            // Re-setup event listeners if chat manager already exists
            this.chatManager.setupEventListeners();
        }

        // Focus on message input
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            setTimeout(() => messageInput.focus(), 100);
        }

        this.state.setState('currentView', 'chat');
    }

    showLearnMore() {
        // Simple alert for now
        this.notifications.info(
            'Cura AI is an advanced medical assistant powered by artificial intelligence. It provides general health information and guidance, but always consult with healthcare professionals for serious medical concerns.',
            { title: 'About Cura AI', duration: 8000 }
        );
    }

    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });

        // Show requested view
        const targetView = document.getElementById(`${viewName}View`);
        if (targetView) {
            targetView.classList.add('active');
        }

        this.state.setState('currentView', viewName);
    }

    toggleTheme() {
        const currentTheme = this.state.settings.theme;
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        this.state.settings.theme = newTheme;
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle?.querySelector('.material-symbols-rounded');
        if (icon) {
            icon.textContent = newTheme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }
}

// Initialize the application
let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new CuraApp();
    
    // Add some initial animations
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);
});

// Export for global access
window.CuraApp = CuraApp;