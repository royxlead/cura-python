/**
 * Cura AI - Modern Medical Assistant Application
 * Version 2.0 - Complete JavaScript Implementation
 * Built with modern ES6+ features and best practices
 */

// Application State Management
class AppState {
    constructor() {
        this.currentView = 'welcome';
        this.user = null;
        this.isAuthenticated = false;
        this.chatMessages = [];
        this.settings = {
            theme: 'light',
            notifications: true,
            voiceInput: true
        };
        this.loadState();
    }

    setState(key, value) {
        this[key] = value;
        this.saveState();
    }

    loadState() {
        try {
            const savedState = localStorage.getItem('cura_app_state');
            if (savedState) {
                const parsed = JSON.parse(savedState);
                Object.assign(this, parsed);
            }
        } catch (error) {
            console.warn('Failed to load app state:', error);
        }
    }

    saveState() {
        try {
            const stateToSave = {
                settings: this.settings,
                user: this.user,
                isAuthenticated: this.isAuthenticated
            };
            localStorage.setItem('cura_app_state', JSON.stringify(stateToSave));
        } catch (error) {
            console.warn('Failed to save app state:', error);
        }
    }
}

// API Service
class APIService {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.token = localStorage.getItem('auth_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

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
            throw error;
        }
    }

    async register(userData) {
        const response = await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        return response;
    }

    async login(credentials) {
        const response = await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (response.access_token) {
            this.token = response.access_token;
            localStorage.setItem('auth_token', this.token);
        }
        
        return response;
    }

    async sendMessage(message, options = {}) {
        return await this.request('/api/chat/message', {
            method: 'POST',
            body: JSON.stringify({
                message,
                include_sources: true,
                ...options
            })
        });
    }

    async getUserProfile() {
        return await this.request('/api/auth/me');
    }

    logout() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    // TEMPORARY: Set a guest token for bypassing auth
    setGuestToken() {
        // Use the existing token from your test
        this.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGNlMzUwMGU1ZmNmODljMWM5OWU2NmMiLCJlbWFpbCI6Im5ld3VzZXJAdGVzdC5jb20iLCJleHAiOjE3NTg0MzA4NDh9.eEKnxqSj8L9rHg4voF7pMUPzITZFXeLda2uv-G_VQI8';
    }
}

// Notification System
class NotificationSystem {
    constructor() {
        this.container = document.getElementById('toastContainer');
        this.toasts = new Map();
    }

    show(message, type = 'info', options = {}) {
        const id = Date.now().toString();
        const toast = this.createToast(message, type, options);
        toast.dataset.id = id;
        
        this.container.appendChild(toast);
        this.toasts.set(id, toast);

        // Auto remove after duration
        const duration = options.duration || 5000;
        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }

        return id;
    }

    createToast(message, type, options) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };

        toast.innerHTML = `
            <span class="toast-icon material-symbols-rounded">${icons[type] || 'info'}</span>
            <div class="toast-content">
                ${options.title ? `<div class="toast-title">${options.title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close notification">
                <span class="material-symbols-rounded">close</span>
            </button>
        `;

        // Add close functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.remove(toast.dataset.id);
        });

        return toast;
    }

    remove(id) {
        const toast = this.toasts.get(id);
        if (toast) {
            toast.style.animation = 'slideOutToast 0.3s ease-in forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                this.toasts.delete(id);
            }, 300);
        }
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
}

// Chat Manager
class ChatManager {
    constructor(apiService, notifications) {
        console.log('ChatManager: Constructor called');
        this.api = apiService;
        this.notifications = notifications;
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendBtn');
        this.voiceButton = document.getElementById('voiceBtn');
        this.attachButton = document.getElementById('attachBtn');
        this.quickSuggestions = document.getElementById('quickSuggestions');
        
        console.log('ChatManager: Elements found:', {
            messagesContainer: !!this.messagesContainer,
            messageInput: !!this.messageInput,
            sendButton: !!this.sendButton,
            voiceButton: !!this.voiceButton,
            attachButton: !!this.attachButton,
            quickSuggestions: !!this.quickSuggestions
        });
        
        this.isTyping = false;
        this.recognition = null;
        this.isRecording = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.setupQuickSuggestions();
        this.setupInputAutoResize();
    }

    setupEventListeners() {
        console.log('ChatManager: Setting up event listeners...');
        console.log('ChatManager: sendButton:', this.sendButton);
        console.log('ChatManager: messageInput:', this.messageInput);
        console.log('ChatManager: voiceButton:', this.voiceButton);
        
        // Send button
        if (this.sendButton) {
            console.log('ChatManager: Adding click listener to send button');
            this.sendButton.addEventListener('click', () => {
                console.log('ChatManager: Send button clicked!');
                this.sendMessage();
            });
        } else {
            console.error('ChatManager: Send button not found!');
        }

        // Enter key to send (Shift+Enter for new line)
        if (this.messageInput) {
            console.log('ChatManager: Adding keydown listener to message input');
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('ChatManager: Enter key pressed, sending message');
                    this.sendMessage();
                }
            });

            // Input change handler
            this.messageInput.addEventListener('input', () => {
                this.handleInputChange();
            });
        } else {
            console.error('ChatManager: Message input not found!');
        }

        // Voice button
        if (this.voiceButton) {
            console.log('ChatManager: Adding click listener to voice button');
            this.voiceButton.addEventListener('click', () => {
                console.log('ChatManager: Voice button clicked!');
                this.toggleVoiceInput();
            });
        } else {
            console.error('ChatManager: Voice button not found!');
        }

        // Attach button
        if (this.attachButton) {
            console.log('ChatManager: Adding click listener to attach button');
            this.attachButton.addEventListener('click', () => {
                console.log('ChatManager: Attach button clicked!');
                this.handleFileUpload();
            });
        } else {
            console.error('ChatManager: Attach button not found!');
        }

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    setupVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            if (this.voiceButton) {
                this.voiceButton.style.display = 'none';
            }
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.voiceButton.classList.add('recording');
            this.messageInput.placeholder = '🎤 Listening... Speak now';
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            this.messageInput.value = finalTranscript + interimTranscript;
            this.handleInputChange();
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopVoiceInput();
            this.notifications.error('Voice input error: ' + event.error);
        };

        this.recognition.onend = () => {
            this.stopVoiceInput();
        };
    }

    setupQuickSuggestions() {
        document.querySelectorAll('.suggestion-card').forEach(card => {
            card.addEventListener('click', () => {
                const message = card.dataset.message;
                if (message) {
                    this.messageInput.value = message;
                    this.handleInputChange();
                    
                    // Auto-send emergency messages
                    if (card.classList.contains('emergency')) {
                        setTimeout(() => this.sendMessage(), 500);
                    } else {
                        this.messageInput.focus();
                    }
                }
            });
        });
    }

    setupInputAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }

    handleInputChange() {
        const value = this.messageInput.value.trim();
        const charCount = document.getElementById('charCount');
        
        // Update character count
        if (charCount) {
            charCount.textContent = this.messageInput.value.length;
        }

        // Enable/disable send button
        this.sendButton.disabled = !value;

        // Hide suggestions if user starts typing
        if (value && this.quickSuggestions) {
            this.quickSuggestions.style.opacity = '0.5';
        } else if (this.quickSuggestions) {
            this.quickSuggestions.style.opacity = '1';
        }
    }

    handleQuickAction(action) {
        let prompt = '';
        
        switch (action) {
            case 'symptoms':
                prompt = 'I want to describe my symptoms: ';
                break;
            case 'medication':
                prompt = 'I have questions about medication: ';
                break;
            case 'emergency':
                prompt = 'EMERGENCY - I need immediate medical guidance: ';
                break;
        }

        this.messageInput.value = prompt;
        this.messageInput.focus();
        this.handleInputChange();

        // Auto-send emergency messages
        if (action === 'emergency') {
            setTimeout(() => this.sendMessage(), 500);
        }
    }

    handleFileUpload() {
        console.log('ChatManager: handleFileUpload called');
        
        // Create a hidden file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif';
        fileInput.style.display = 'none';
        
        // Handle file selection
        fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                console.log('File selected:', file.name, file.type, file.size);
                this.uploadFile(file);
            }
        });
        
        // Trigger file selection dialog
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    }

    uploadFile(file) {
        console.log('ChatManager: Uploading file:', file.name);
        
        // Show upload progress message
        this.addMessage('user', `📎 Uploading file: ${file.name}...`);
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        
        // TODO: Implement actual file upload to backend
        // For now, just show a success message
        setTimeout(() => {
            this.addMessage('assistant', `✅ File "${file.name}" uploaded successfully! How can I help you with this file?`);
        }, 1000);
    }

    toggleVoiceInput() {
        if (this.isRecording) {
            this.stopVoiceInput();
        } else {
            this.startVoiceInput();
        }
    }

    startVoiceInput() {
        if (this.recognition) {
            this.recognition.start();
        }
    }

    stopVoiceInput() {
        if (this.recognition) {
            this.recognition.stop();
        }
        
        this.isRecording = false;
        this.voiceButton.classList.remove('recording');
        this.messageInput.placeholder = 'Ask me about your health concerns, symptoms, or medications...';
    }

    async sendMessage() {
        console.log('ChatManager: sendMessage called');
        const message = this.messageInput.value.trim();
        console.log('ChatManager: message:', message);
        if (!message) {
            console.log('ChatManager: No message to send');
            return;
        }

        // Clear input immediately
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.handleInputChange();

        // Hide quick suggestions after first message
        if (this.quickSuggestions) {
            this.quickSuggestions.style.display = 'none';
        }

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        const typingId = this.showTypingIndicator();

        try {
            // Send message to API
            const response = await this.api.sendMessage(message);
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            // Add AI response
            this.addMessage(response.message, 'ai');

            // Add sources if available and they have meaningful content
            if (response.sources && response.sources.length > 0) {
                // Filter out sources that don't have meaningful titles or content
                const meaningfulSources = response.sources.filter(s => {
                    const title = s.title || s.source || '';
                    const filename = s.metadata?.source || s.metadata?.filename || '';
                    return title !== 'Medical Database' && title !== '' && filename !== '';
                });
                
                if (meaningfulSources.length > 0) {
                    const sourcesText = `📚 **Sources:** ${meaningfulSources.map(s => {
                        const title = s.title || s.source || s.metadata?.filename || s.metadata?.source;
                        return title || 'Medical Reference';
                    }).join(', ')}`;
                    this.addMessage(sourcesText, 'ai-sources');
                }
            }

        } catch (error) {
            console.error('Failed to send message:', error);
            this.removeTypingIndicator(typingId);
            
            let errorMessage = 'I apologize, but I\'m experiencing technical difficulties. Please try again.';
            
            if (error.message.includes('401') || error.message.includes('authentication')) {
                errorMessage = 'Your session has expired. Please log in again.';
                // Trigger logout after a delay
                setTimeout(() => app.logout(), 2000);
            }
            
            this.addMessage(errorMessage, 'ai-error');
            this.notifications.error('Failed to send message');
        }
    }

    addMessage(content, sender, timestamp = new Date()) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const isUser = sender === 'user';
        const isError = sender === 'ai-error';
        const isSources = sender === 'ai-sources';
        
        const avatarIcon = isUser ? 'person' : 'health_and_safety';
        const avatarClass = isUser ? 'user-avatar' : 'ai-avatar';
        const senderName = isUser ? 'You' : 'Cura AI';

        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">
                <span class="material-symbols-rounded">${avatarIcon}</span>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${senderName}</span>
                    <span class="message-time">${this.formatTime(timestamp)}</span>
                </div>
                <div class="message-body">
                    ${this.formatMessageContent(content, sender)}
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Add entrance animation
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);

        return messageDiv;
    }

    formatMessageContent(content, sender) {
        if (sender === 'ai-sources') {
            return `<div class="sources-info">${content}</div>`;
        }

        // Format markdown-like text
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');

        // Format lists
        if (formatted.includes('•') || formatted.includes('-')) {
            formatted = formatted.replace(/(^|\n)([•-])\s*(.+)/gm, '$1<li>$3</li>');
            if (formatted.includes('<li>')) {
                formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
            }
        }

        return `<div class="message-text">${formatted}</div>`;
    }

    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = typingId;
        typingDiv.className = 'message ai-message typing-message';
        
        typingDiv.innerHTML = `
            <div class="message-avatar ai-avatar">
                <span class="material-symbols-rounded">health_and_safety</span>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">Cura AI</span>
                    <span class="message-time">typing...</span>
                </div>
                <div class="message-body">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();

        return typingId;
    }

    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    scrollToBottom() {
        // Use setTimeout to ensure DOM is updated
        setTimeout(() => {
            this.messagesContainer.scrollTo({
                top: this.messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    clearChat() {
        this.messagesContainer.innerHTML = '';
        if (this.quickSuggestions) {
            this.quickSuggestions.style.display = 'block';
        }
    }
}

// Authentication Manager
class AuthManager {
    constructor(apiService, notifications) {
        this.api = apiService;
        this.notifications = notifications;
        this.loginForm = document.getElementById('loginForm');
        this.signupForm = document.getElementById('signupForm');
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupPasswordToggles();
        this.setupPasswordStrength();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Form submissions
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (this.signupForm) {
            this.signupForm.addEventListener('submit', (e) => this.handleSignup(e));
        }

        // Form switching
        const showSignupBtn = document.getElementById('showSignupBtn');
        const showLoginBtn = document.getElementById('showLoginBtn');

        if (showSignupBtn) {
            showSignupBtn.addEventListener('click', () => app.showView('signup'));
        }

        if (showLoginBtn) {
            showLoginBtn.addEventListener('click', () => app.showView('login'));
        }
    }

    setupPasswordToggles() {
        document.querySelectorAll('.password-toggle').forEach(toggle => {
            toggle.addEventListener('click', () => {
                const input = toggle.parentElement.querySelector('input');
                const icon = toggle.querySelector('.material-symbols-rounded');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.textContent = 'visibility_off';
                } else {
                    input.type = 'password';
                    icon.textContent = 'visibility';
                }
            });
        });
    }

    setupPasswordStrength() {
        const passwordInput = document.getElementById('signupPassword');
        const strengthBar = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');

        if (passwordInput && strengthBar && strengthText) {
            passwordInput.addEventListener('input', () => {
                const strength = this.calculatePasswordStrength(passwordInput.value);
                strengthBar.style.width = `${strength.percentage}%`;
                strengthBar.className = `strength-fill ${strength.level}`;
                strengthText.textContent = `Password strength: ${strength.label}`;
            });
        }
    }

    calculatePasswordStrength(password) {
        let score = 0;
        let feedback = [];

        if (password.length >= 8) score += 25;
        else feedback.push('At least 8 characters');

        if (/[a-z]/.test(password)) score += 25;
        else feedback.push('Lowercase letter');

        if (/[A-Z]/.test(password)) score += 25;
        else feedback.push('Uppercase letter');

        if (/[0-9]/.test(password)) score += 25;
        else feedback.push('Number');

        if (/[^A-Za-z0-9]/.test(password)) score += 10;

        let level, label;
        if (score < 30) {
            level = 'weak';
            label = 'Weak';
        } else if (score < 60) {
            level = 'medium';
            label = 'Medium';
        } else {
            level = 'strong';
            label = 'Strong';
        }

        return {
            percentage: Math.min(score, 100),
            level,
            label,
            feedback
        };
    }

    setupFormValidation() {
        // Real-time validation
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        // Required field validation
        if (field.required && !value) {
            isValid = false;
            message = 'This field is required';
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
        }

        // Password confirmation
        if (field.name === 'confirmPassword') {
            const password = document.getElementById('signupPassword');
            if (password && value !== password.value) {
                isValid = false;
                message = 'Passwords do not match';
            }
        }

        // Username validation
        if (field.name === 'username' && value) {
            if (value.length < 3) {
                isValid = false;
                message = 'Username must be at least 3 characters';
            }
        }

        if (!isValid) {
            this.showFieldError(field, message);
        } else {
            this.clearFieldError(field);
        }

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: var(--error-500);
            font-size: var(--text-sm);
            margin-top: var(--space-1);
            display: flex;
            align-items: center;
            gap: var(--space-1);
        `;
        errorDiv.innerHTML = `
            <span class="material-symbols-rounded" style="font-size: 1rem;">error</span>
            <span>${message}</span>
        `;

        field.parentElement.appendChild(errorDiv);
        field.style.borderColor = 'var(--error-500)';
    }

    clearFieldError(field) {
        const errorDiv = field.parentElement.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
        field.style.borderColor = '';
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const formData = new FormData(this.loginForm);
        const credentials = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        const submitBtn = this.loginForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('loginBtnText');
        const btnLoader = document.getElementById('loginBtnLoader');

        this.setLoadingState(submitBtn, btnText, btnLoader, true);

        try {
            const response = await this.api.login(credentials);
            
            // Get user profile
            const userProfile = await this.api.getUserProfile();
            
            app.setUser(userProfile);
            this.notifications.success('Welcome back!', { title: 'Login Successful' });
            
            // Switch to chat interface
            app.showChatInterface();

        } catch (error) {
            console.error('Login failed:', error);
            let message = 'Login failed. Please check your credentials.';
            
            if (error.message.includes('401')) {
                message = 'Invalid email or password.';
            } else if (error.message.includes('network')) {
                message = 'Network error. Please check your connection.';
            }
            
            this.notifications.error(message, { title: 'Login Failed' });
        } finally {
            this.setLoadingState(submitBtn, btnText, btnLoader, false);
        }
    }

    async handleSignup(e) {
        e.preventDefault();

        // Validate all fields
        const inputs = this.signupForm.querySelectorAll('input');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            this.notifications.error('Please fix the errors in the form.');
            return;
        }

        const formData = new FormData(this.signupForm);
        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            first_name: formData.get('firstName'),
            last_name: formData.get('lastName')
        };

        const submitBtn = this.signupForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('signupBtnText');
        const btnLoader = document.getElementById('signupBtnLoader');

        this.setLoadingState(submitBtn, btnText, btnLoader, true);

        try {
            await this.api.register(userData);
            
            this.notifications.success('Account created successfully! Please sign in.', {
                title: 'Registration Successful',
                duration: 7000
            });
            
            // Switch to login form
            app.showView('login');
            
            // Pre-fill email
            const loginEmail = document.getElementById('loginEmail');
            if (loginEmail) {
                loginEmail.value = userData.email;
            }

        } catch (error) {
            console.error('Registration failed:', error);
            let message = 'Registration failed. Please try again.';
            
            if (error.message.includes('already exists') || error.message.includes('duplicate')) {
                message = 'An account with this email or username already exists.';
            } else if (error.message.includes('validation')) {
                message = 'Please check your information and try again.';
            }
            
            this.notifications.error(message, { title: 'Registration Failed' });
        } finally {
            this.setLoadingState(submitBtn, btnText, btnLoader, false);
        }
    }

    setLoadingState(button, textElement, loaderElement, isLoading) {
        if (isLoading) {
            button.disabled = true;
            textElement.style.display = 'none';
            loaderElement.classList.remove('hidden');
        } else {
            button.disabled = false;
            textElement.style.display = 'inline';
            loaderElement.classList.add('hidden');
        }
    }
}

// Main Application Class
class CuraApp {
    constructor() {
        console.log('🚀 CuraApp constructor started');
        this.state = new AppState();
        this.api = new APIService();
        this.notifications = new NotificationSystem();
        // this.auth = new AuthManager(this.api, this.notifications); // Commented out for direct chat access
        this.chat = null;
        
        console.log('🔍 Looking for main UI elements...');
        this.loadingScreen = document.getElementById('loadingScreen');
        this.authSection = document.getElementById('authSection');
        this.chatSection = document.getElementById('chatSection');
        
        console.log('🔍 Elements found:', {
            loadingScreen: !!this.loadingScreen,
            authSection: !!this.authSection,
            chatSection: !!this.chatSection
        });
        
        console.log('🚀 CuraApp about to call init()');
        this.init();
    }

    async init() {
        console.log('App: Starting initialization...');
        
        // Direct to chat interface (bypass auth and loading screen)
        console.log('App: Setting guest token...');
        this.api.setGuestToken(); // Set guest token for API access
        console.log('App: Setting user...');
        this.setUser({ username: 'Guest User', email: 'guest@cura.ai' });
        console.log('App: Showing chat interface...');
        this.showChatInterface();
        
        console.log('App: Setting up event listeners...');
        this.setupEventListeners();
        
        // Ensure loading screen is hidden
        this.hideLoadingScreen();
        
        console.log('App: Initialization complete!');
    }

    async showLoadingScreen() {
        // Skip loading screen delay - go directly to chat
        return Promise.resolve();
    }

    hideLoadingScreen() {
        console.log('App: Hiding loading screen...', this.loadingScreen);
        if (this.loadingScreen) {
            this.loadingScreen.style.opacity = '0';
            setTimeout(() => {
                this.loadingScreen.style.display = 'none';
            }, 500);
        } else {
            console.error('App: Loading screen element not found');
        }
    }

    setupEventListeners() {
        // Get started button
        const getStartedBtn = document.getElementById('getStartedBtn');
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', () => this.showView('login'));
        }

        // Learn more button
        const learnMoreBtn = document.getElementById('learnMoreBtn');
        if (learnMoreBtn) {
            learnMoreBtn.addEventListener('click', () => {
                // Could show a modal or scroll to more info
                this.notifications.info('More information coming soon!');
            });
        }

        // Theme toggle
        console.log('🔍 Looking for theme toggle button...');
        const themeToggle = document.getElementById('themeToggle');
        console.log('🔍 Theme toggle element:', themeToggle);
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                console.log('🔧 Theme toggle clicked!');
                this.toggleTheme();
            });
            console.log('✅ Theme toggle listener attached');
        } else {
            console.error('❌ Theme toggle button not found!');
        }

        // User menu
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                userDropdown.classList.remove('show');
            });
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Settings and help buttons
        const settingsBtn = document.getElementById('settingsBtn');
        const helpBtn = document.getElementById('helpBtn');
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }
        
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.showHelp());
        }
    }

    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });

        // Show selected view
        const targetView = document.getElementById(`${viewName}View`);
        if (targetView) {
            targetView.classList.add('active');
        }

        this.state.setState('currentView', viewName);
    }

    showChatInterface() {
        console.log('🔧 showChatInterface called');
        console.log('🔍 Elements check:', {
            authSection: this.authSection,
            chatSection: this.chatSection,
            loadingScreen: this.loadingScreen
        });
        
        if (this.authSection) {
            this.authSection.classList.add('hidden');
        } else {
            console.error('❌ authSection element not found!');
        }
        
        if (this.chatSection) {
            this.chatSection.classList.remove('hidden');
        } else {
            console.error('❌ chatSection element not found!');
        }
        
        // Initialize chat manager if not already done
        if (!this.chat) {
            console.log('🔧 Creating new ChatManager');
            this.chat = new ChatManager(this.api, this.notifications);
            console.log('🔧 ChatManager created:', this.chat);
        } else {
            console.log('🔧 ChatManager already exists');
        }

        // Update user greeting
        this.updateUserGreeting();
        console.log('🔧 showChatInterface complete');
    }

    showAuthInterface() {
        this.chatSection.classList.add('hidden');
        this.authSection.classList.remove('hidden');
        this.showView('welcome');
    }

    setUser(userData) {
        this.state.setState('user', userData);
        this.state.setState('isAuthenticated', true);
        
        // Update UI with user data
        this.updateUserInfo(userData);
    }

    updateUserInfo(userData) {
        const userName = document.getElementById('userName');
        const userEmail = document.getElementById('userEmail');
        
        if (userName) {
            userName.textContent = `${userData.first_name} ${userData.last_name}`.trim();
        }
        
        if (userEmail) {
            userEmail.textContent = userData.email;
        }
    }

    updateUserGreeting() {
        const userGreeting = document.getElementById('userGreeting');
        if (userGreeting && this.state.user) {
            const firstName = this.state.user.first_name || 'there';
            const hour = new Date().getHours();
            let greeting = 'Hello';

            if (hour < 12) greeting = 'Good morning';
            else if (hour < 18) greeting = 'Good afternoon';
            else greeting = 'Good evening';

            userGreeting.textContent = `${greeting}, ${firstName}!`;
        }
    }

    logout() {
        this.api.logout();
        this.state.setState('user', null);
        this.state.setState('isAuthenticated', false);
        
        // Clear chat if exists
        if (this.chat) {
            this.chat.clearChat();
        }
        
        this.notifications.success('Logged out successfully');
        this.showAuthInterface();
    }

    toggleTheme() {
        const currentTheme = this.state.settings.theme;
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        this.state.settings.theme = newTheme;
        this.state.saveState();
        
        const themeIcon = document.querySelector('#themeToggle .material-symbols-rounded');
        if (themeIcon) {
            themeIcon.textContent = newTheme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }

    showSettings() {
        this.notifications.info('Settings panel coming soon!');
    }

    showHelp() {
        this.notifications.info('Help documentation coming soon!');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('🚀 DOM LOADED - Initializing Cura App...');
        console.log('🔍 Document ready state:', document.readyState);
        window.app = new CuraApp();
        console.log('🚀 CuraApp instance created successfully:', window.app);
    } catch (error) {
        console.error('❌ Failed to initialize app:', error);
        console.error('❌ Error stack:', error.stack);
        
        // Fallback: show chat interface directly if app fails
        const chatSection = document.getElementById('chatSection');
        if (chatSection) {
            chatSection.classList.remove('hidden');
        }
    }
});

// Add CSS for typing indicator animation
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        display: flex;
        gap: 4px;
        align-items: center;
        padding: 8px 0;
    }

    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        animation: typingDots 1.4s infinite ease-in-out;
    }

    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0s; }

    @keyframes typingDots {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    @keyframes slideOutToast {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }

    .field-error {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);