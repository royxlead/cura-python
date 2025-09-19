/**
 * Cura Medical AI Assistant - Modern JavaScript Application
 * Version 3.0 - Complete rewrite with modern patterns
 */

class CuraApp {
    constructor() {
        this.isAuthenticated = false;
        this.currentUser = null;
        this.currentSession = null;
        this.websocket = null;
        this.currentView = 'chat';
        this.theme = localStorage.getItem('cura-theme') || 'light';
        
        this.init();
    }

    async init() {
        this.showLoading();
        
        // Check authentication
        await this.checkAuth();
        
        // Initialize app
        if (this.isAuthenticated) {
            this.hideLoading();
            this.showApp();
            this.initializeApp();
        } else {
            this.hideLoading();
            this.showAuthModal();
        }
        
        // Initialize service worker
        this.initServiceWorker();
        
        // Setup PWA install prompt
        this.setupPWAPrompt();
    }

    showLoading() {
        document.getElementById('loadingScreen').classList.remove('hidden');
        
        // Animate loading progress
        const progress = document.querySelector('.loading-progress');
        if (progress) {
            setTimeout(() => progress.style.width = '100%', 500);
        }
    }

    hideLoading() {
        setTimeout(() => {
            document.getElementById('loadingScreen').classList.add('hidden');
        }, 1000);
    }

    async checkAuth() {
        const token = localStorage.getItem('cura-auth-token');
        if (!token) return;

        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.currentUser = await response.json();
                this.isAuthenticated = true;
            } else {
                localStorage.removeItem('cura-auth-token');
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('cura-auth-token');
        }
    }

    showApp() {
        document.getElementById('app').classList.remove('hidden');
        this.applyTheme();
    }

    showAuthModal() {
        const modal = document.getElementById('authModal');
        modal.classList.add('show');
        this.setupAuthModal();
    }

    hideAuthModal() {
        document.getElementById('authModal').classList.remove('show');
    }

    setupAuthModal() {
        const form = document.getElementById('authForm');
        const switchBtn = document.getElementById('authSwitchBtn');
        const title = document.getElementById('authTitle');
        const subtitle = document.getElementById('authSubtitle');
        const submitBtn = document.getElementById('authSubmitBtn');
        const registerFields = document.getElementById('registerFields');
        const switchText = document.getElementById('authSwitchText');
        
        let isLogin = true;

        const toggleMode = () => {
            isLogin = !isLogin;
            
            if (isLogin) {
                title.textContent = 'Welcome Back';
                subtitle.textContent = 'Sign in to your account';
                submitBtn.textContent = 'Sign In';
                switchText.textContent = "Don't have an account?";
                switchBtn.textContent = 'Sign up';
                registerFields.classList.add('hidden');
            } else {
                title.textContent = 'Create Account';
                subtitle.textContent = 'Join Cura today';
                submitBtn.textContent = 'Create Account';
                switchText.textContent = 'Already have an account?';
                switchBtn.textContent = 'Sign in';
                registerFields.classList.remove('hidden');
            }
        };

        switchBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleMode();
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            try {
                submitBtn.disabled = true;
                submitBtn.textContent = isLogin ? 'Signing in...' : 'Creating account...';
                
                const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    localStorage.setItem('cura-auth-token', result.token.access_token);
                    this.currentUser = result.user;
                    this.isAuthenticated = true;
                    this.hideAuthModal();
                    this.showApp();
                    this.initializeApp();
                    this.showToast('Welcome to Cura!', 'success');
                } else {
                    this.showToast(result.detail || 'Authentication failed', 'error');
                }
            } catch (error) {
                this.showToast('Connection error. Please try again.', 'error');
                console.error('Auth error:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = isLogin ? 'Sign In' : 'Create Account';
            }
        });
    }

    initializeApp() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.setupNavigation();
        this.setupChat();
        this.setupVoiceInterface();
        this.setupSymptomChecker();
    }

    setupEventListeners() {
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('show');
        });

        // User menu
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        document.addEventListener('click', () => {
            userDropdown.classList.remove('show');
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.logout();
        });

        // Close sidebar on mobile when clicking outside
        document.addEventListener('click', (e) => {
            const sidebar = document.getElementById('sidebar');
            const sidebarToggle = document.getElementById('sidebarToggle');
            
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                const view = item.dataset.view;
                if (view) {
                    this.switchView(view);
                    
                    // Update active nav item
                    navItems.forEach(nav => nav.classList.remove('active'));
                    item.classList.add('active');
                    
                    // Close sidebar on mobile
                    document.getElementById('sidebar').classList.remove('show');
                }
            });
        });
    }

    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show selected view
        const targetView = document.getElementById(`${viewName}View`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
        }
    }

    setupChat() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatMessages = document.getElementById('chatMessages');
        
        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });

        // Send message on Enter (but allow Shift+Enter for new lines)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                if (message) {
                    messageInput.value = message;
                    this.sendMessage();
                }
            });
        });

        // Voice input button
        document.getElementById('voiceInputBtn').addEventListener('click', () => {
            this.startVoiceInput();
        });

        // Attach file button
        document.getElementById('attachBtn').addEventListener('click', () => {
            this.attachFile();
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Add user message to chat
        this.addMessageToChat('user', message);

        // Show typing indicator
        const typingIndicator = this.addTypingIndicator();

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('cura-auth-token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSession,
                    include_sources: true
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.currentSession = result.session_id;
                this.removeTypingIndicator(typingIndicator);
                this.addMessageToChat('assistant', result.message, result.sources);
            } else {
                this.removeTypingIndicator(typingIndicator);
                this.addMessageToChat('assistant', 'I apologize, but I encountered an error. Please try again.');
                this.showToast(result.detail || 'Failed to send message', 'error');
            }
        } catch (error) {
            this.removeTypingIndicator(typingIndicator);
            this.addMessageToChat('assistant', 'I apologize, but I\'m having trouble connecting. Please check your internet connection and try again.');
            console.error('Send message error:', error);
        }
    }

    addMessageToChat(role, content, sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        
        // Remove welcome message if it exists
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' 
            ? '<span class="material-symbols-rounded">person</span>'
            : '<span class="material-symbols-rounded">health_and_safety</span>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = content;
        
        const footerDiv = document.createElement('div');
        footerDiv.className = 'message-footer';
        footerDiv.innerHTML = `
            <span>${new Date().toLocaleTimeString()}</span>
            ${sources && sources.length > 0 ? `<span>${sources.length} sources</span>` : ''}
        `;

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(footerDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    addTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <span class="material-symbols-rounded">health_and_safety</span>
            </div>
            <div class="message-content">
                <div class="typing-animation">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return typingDiv;
    }

    removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.remove();
        }
    }

    setupWebSocket() {
        if (!this.currentUser) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/chat/ws/${this.currentUser.id}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'response') {
                this.addMessageToChat('assistant', data.message, data.sources || []);
            }
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.setupWebSocket(), 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    setupVoiceInterface() {
        const voiceStartBtn = document.getElementById('voiceStartBtn');
        const voiceStopBtn = document.getElementById('voiceStopBtn');
        const voiceStatus = document.getElementById('voiceStatus');
        const voiceTranscript = document.getElementById('voiceTranscript');
        const voiceResponse = document.getElementById('voiceResponse');
        
        let recognition = null;
        let isRecording = false;

        // Check for speech recognition support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isRecording = true;
                voiceStatus.textContent = 'Listening...';
                voiceStartBtn.classList.add('hidden');
                voiceStopBtn.classList.remove('hidden');
                document.querySelector('.voice-circle').classList.add('recording');
                document.querySelector('.sound-waves').classList.add('active');
            };

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                voiceTranscript.textContent = transcript;
            };

            recognition.onend = async () => {
                isRecording = false;
                voiceStatus.textContent = 'Processing...';
                voiceStartBtn.classList.remove('hidden');
                voiceStopBtn.classList.add('hidden');
                document.querySelector('.voice-circle').classList.remove('recording');
                document.querySelector('.sound-waves').classList.remove('active');
                
                const transcript = voiceTranscript.textContent;
                if (transcript.trim()) {
                    await this.processVoiceInput(transcript);
                }
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                voiceStatus.textContent = 'Error occurred. Please try again.';
                this.resetVoiceInterface();
            };
        }

        voiceStartBtn.addEventListener('click', () => {
            if (recognition) {
                recognition.start();
            } else {
                this.showToast('Speech recognition not supported in your browser', 'error');
            }
        });

        voiceStopBtn.addEventListener('click', () => {
            if (recognition && isRecording) {
                recognition.stop();
            }
        });

        // Voice response playback
        document.getElementById('playResponseBtn').addEventListener('click', () => {
            this.playVoiceResponse();
        });

        document.getElementById('newVoiceBtn').addEventListener('click', () => {
            this.resetVoiceInterface();
        });
    }

    async processVoiceInput(transcript) {
        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('cura-auth-token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: transcript,
                    session_id: this.currentSession,
                    include_sources: true
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.currentSession = result.session_id;
                document.getElementById('voiceStatus').textContent = 'Response ready';
                document.getElementById('voiceResponseText').textContent = result.message;
                document.getElementById('voiceResponse').classList.remove('hidden');
            } else {
                throw new Error(result.detail || 'Failed to process voice input');
            }
        } catch (error) {
            document.getElementById('voiceStatus').textContent = 'Error processing request';
            console.error('Voice processing error:', error);
        }
    }

    playVoiceResponse() {
        const responseText = document.getElementById('voiceResponseText').textContent;
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(responseText);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            speechSynthesis.speak(utterance);
        } else {
            this.showToast('Speech synthesis not supported', 'error');
        }
    }

    resetVoiceInterface() {
        document.getElementById('voiceStatus').textContent = 'Tap to speak';
        document.getElementById('voiceTranscript').textContent = 'Your voice will appear here...';
        document.getElementById('voiceResponse').classList.add('hidden');
        document.getElementById('voiceStartBtn').classList.remove('hidden');
        document.getElementById('voiceStopBtn').classList.add('hidden');
    }

    setupSymptomChecker() {
        const analyzeBtn = document.getElementById('analyzeSymptoms');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', async () => {
                await this.analyzeSymptoms();
            });
        }
    }

    async analyzeSymptoms() {
        const name = document.getElementById('symptomName').value.trim();
        const severity = document.getElementById('symptomSeverity').value;
        const duration = document.getElementById('symptomDuration').value;
        const description = document.getElementById('symptomDescription').value.trim();

        if (!name) {
            this.showToast('Please enter a symptom name', 'error');
            return;
        }

        const analyzeBtn = document.getElementById('analyzeSymptoms');
        const resultsSection = document.getElementById('symptomResults');
        const analysisContent = document.getElementById('symptomAnalysis');

        try {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="material-symbols-rounded">hourglass_empty</span> Analyzing...';

            // Create symptom object
            const symptom = {
                name: name,
                severity: severity,
                duration_hours: duration ? parseInt(duration) : null,
                description: description
            };

            // For now, use the chat API to analyze symptoms
            const message = `Please analyze this symptom: ${name} (severity: ${severity}${duration ? `, duration: ${duration} hours` : ''}${description ? `, details: ${description}` : ''})`;

            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('cura-auth-token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSession,
                    include_sources: true
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.currentSession = result.session_id;
                analysisContent.innerHTML = `
                    <div class="analysis-result">
                        <h4>AI Analysis</h4>
                        <p>${result.message}</p>
                        ${result.sources && result.sources.length > 0 ? 
                            `<div class="sources">
                                <h5>Sources:</h5>
                                <ul>
                                    ${result.sources.map(source => `<li>${source.content}</li>`).join('')}
                                </ul>
                            </div>` : ''
                        }
                        <div class="disclaimer">
                            <strong>Medical Disclaimer:</strong> This analysis is for informational purposes only and should not replace professional medical advice. Please consult with a healthcare professional for proper diagnosis and treatment.
                        </div>
                    </div>
                `;
                resultsSection.classList.remove('hidden');
            } else {
                throw new Error(result.detail || 'Analysis failed');
            }
        } catch (error) {
            this.showToast('Failed to analyze symptoms. Please try again.', 'error');
            console.error('Symptom analysis error:', error);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="material-symbols-rounded">medical_information</span> Analyze Symptoms';
        }
    }

    startVoiceInput() {
        // Switch to voice view and start recording
        this.switchView('voice');
        document.querySelector('[data-view="voice"]').click();
        
        setTimeout(() => {
            document.getElementById('voiceStartBtn').click();
        }, 500);
    }

    attachFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,.pdf,.doc,.docx';
        input.multiple = false;
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileUpload(file);
            }
        };
        
        input.click();
    }

    async handleFileUpload(file) {
        // For now, just show a message that file upload is coming soon
        this.showToast('File upload feature coming soon!', 'info');
        
        // TODO: Implement actual file upload functionality
        console.log('File selected:', file.name, file.type, file.size);
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('cura-theme', this.theme);
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        
        const themeIcon = document.querySelector('#themeToggle .material-symbols-rounded');
        if (themeIcon) {
            themeIcon.textContent = this.theme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }

    logout() {
        localStorage.removeItem('cura-auth-token');
        this.isAuthenticated = false;
        this.currentUser = null;
        this.currentSession = null;
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Hide app and show auth modal
        document.getElementById('app').classList.add('hidden');
        this.showAuthModal();
        
        this.showToast('Logged out successfully', 'info');
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastIcon = toast.querySelector('.toast-icon');
        const toastMessage = toast.querySelector('.toast-message');
        
        // Set icon based on type
        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        
        toastIcon.textContent = icons[type] || icons.info;
        toastMessage.textContent = message;
        
        // Show toast
        toast.classList.add('show');
        
        // Hide after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').onclick = () => {
            toast.classList.remove('show');
        };
    }

    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered');
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    setupPWAPrompt() {
        let deferredPrompt = null;
        const installPrompt = document.getElementById('installPrompt');
        const installBtn = document.getElementById('installBtn');
        const dismissBtn = document.getElementById('dismissInstall');

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install prompt after a delay
            setTimeout(() => {
                installPrompt.classList.add('show');
            }, 3000);
        });

        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const result = await deferredPrompt.userChoice;
                
                if (result.outcome === 'accepted') {
                    this.showToast('App installed successfully!', 'success');
                }
                
                deferredPrompt = null;
                installPrompt.classList.remove('show');
            }
        });

        dismissBtn.addEventListener('click', () => {
            installPrompt.classList.remove('show');
            localStorage.setItem('cura-install-dismissed', 'true');
        });

        // Don't show if previously dismissed
        if (localStorage.getItem('cura-install-dismissed')) {
            return;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.curaApp = new CuraApp();
});

// Export for global access
window.CuraApp = CuraApp;