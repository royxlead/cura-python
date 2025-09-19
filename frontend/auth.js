// Authentication Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAuthPage();
});

function initializeAuthPage() {
    // Form switching
    setupFormSwitching();
    
    // Password toggles
    setupPasswordToggles();
    
    // Password strength checker
    setupPasswordStrength();
    
    // Feature showcase animations
    setupFeatureShowcase();
    
    // Statistics animation
    setupStatsAnimation();
    
    // Demo animations
    setupDemoAnimations();
    
    // Form validation
    setupFormValidation();
    
    // Scroll functionality
    setupScrollProgress();
    setupScrollReveal();
    setupScrollHint();
}

// Form Switching
function setupFormSwitching() {
    const showSignupBtn = document.getElementById('showSignup');
    const showLoginBtn = document.getElementById('showLogin');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    showSignupBtn?.addEventListener('click', () => {
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
    });
    
    showLoginBtn?.addEventListener('click', () => {
        signupForm.classList.remove('active');
        loginForm.classList.add('active');
    });
}

// Password Toggle Functionality
function setupPasswordToggles() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('.material-symbols-rounded');
            
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

// Password Strength Checker
function setupPasswordStrength() {
    const passwordInput = document.getElementById('signupPassword');
    const strengthBar = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');
    
    if (!passwordInput) return;
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = calculatePasswordStrength(password);
        
        strengthBar.style.width = `${strength.percentage}%`;
        strengthText.textContent = `Password strength: ${strength.level}`;
        
        // Color coding
        strengthBar.style.background = strength.color;
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    let level = 'Weak';
    let percentage = 0;
    let color = '#ff4444';
    
    if (password.length >= 8) score += 25;
    if (password.length >= 12) score += 25;
    if (/[a-z]/.test(password)) score += 10;
    if (/[A-Z]/.test(password)) score += 10;
    if (/[0-9]/.test(password)) score += 15;
    if (/[^A-Za-z0-9]/.test(password)) score += 15;
    
    percentage = Math.min(score, 100);
    
    if (percentage >= 80) {
        level = 'Very Strong';
        color = '#00c851';
    } else if (percentage >= 60) {
        level = 'Strong';
        color = '#ffbb33';
    } else if (percentage >= 40) {
        level = 'Medium';
        color = '#ff8800';
    } else if (percentage >= 20) {
        level = 'Weak';
        color = '#ff4444';
    } else {
        level = 'Very Weak';
        color = '#cc0000';
    }
    
    return { percentage, level, color };
}

// Feature Showcase Animations
function setupFeatureShowcase() {
    const featureItems = document.querySelectorAll('.feature-item');
    let currentFeature = 0;
    
    // Auto-rotate features every 3 seconds
    setInterval(() => {
        featureItems.forEach(item => item.classList.remove('active'));
        featureItems[currentFeature].classList.add('active');
        
        currentFeature = (currentFeature + 1) % featureItems.length;
    }, 3000);
    
    // Manual feature selection
    featureItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            featureItems.forEach(f => f.classList.remove('active'));
            item.classList.add('active');
            currentFeature = index;
        });
    });
}

// Statistics Counter Animation
function setupStatsAnimation() {
    const statNumbers = document.querySelectorAll('.stat-number');
    let animated = false;
    
    function animateStats() {
        if (animated) return;
        animated = true;
        
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target'));
            const increment = target / 100;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                if (target >= 1000) {
                    stat.textContent = Math.floor(current).toLocaleString();
                } else {
                    stat.textContent = Math.floor(current);
                }
            }, 20);
        });
    }
    
    // Trigger animation when stats come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
            }
        });
    });
    
    const statsGrid = document.querySelector('.stats-grid');
    if (statsGrid) {
        observer.observe(statsGrid);
    }
}

// Demo Chat Animations
function setupDemoAnimations() {
    const demoMessages = document.querySelectorAll('.demo-message');
    let messageIndex = 0;
    
    // Hide all messages initially
    demoMessages.forEach((msg, index) => {
        if (index > 0) {
            msg.style.display = 'none';
        }
    });
    
    // Show messages one by one
    const showNextMessage = () => {
        if (messageIndex < demoMessages.length - 1) {
            messageIndex++;
            demoMessages[messageIndex].style.display = 'flex';
            demoMessages[messageIndex].style.animation = 'messageSlide 0.5s ease-out';
            
            setTimeout(showNextMessage, 2000);
        } else {
            // Restart the sequence
            setTimeout(() => {
                demoMessages.forEach((msg, index) => {
                    if (index > 0) {
                        msg.style.display = 'none';
                    }
                });
                messageIndex = 0;
                setTimeout(showNextMessage, 1000);
            }, 3000);
        }
    };
    
    // Start the animation sequence
    setTimeout(showNextMessage, 2000);
}

// Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.form-container');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const formType = this.closest('#loginForm') ? 'login' : 'signup';
            
            if (validateForm(this, formType)) {
                handleFormSubmission(formData, formType);
            }
        });
    });
}

function validateForm(form, formType) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(input);
        }
    });
    
    // Email validation
    const emailInput = form.querySelector('input[type="email"]');
    if (emailInput && emailInput.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value)) {
            showFieldError(emailInput, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Password confirmation for signup
    if (formType === 'signup') {
        const password = form.querySelector('#signupPassword').value;
        const confirmPassword = form.querySelector('#confirmPassword').value;
        
        if (password !== confirmPassword) {
            showFieldError(form.querySelector('#confirmPassword'), 'Passwords do not match');
            isValid = false;
        }
        
        // Terms acceptance
        const termsCheckbox = form.querySelector('input[name="terms"]');
        if (!termsCheckbox.checked) {
            showFieldError(termsCheckbox, 'Please accept the terms and conditions');
            isValid = false;
        }
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#ff4444';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.closest('.form-group').appendChild(errorDiv);
    field.closest('.input-group').style.borderColor = '#ff4444';
}

function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    const existingError = formGroup.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.closest('.input-group').style.borderColor = '';
}

function handleFormSubmission(formData, formType) {
    const submitBtn = document.querySelector('.auth-btn.primary');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<span class="material-symbols-rounded spinning">progress_activity</span> Processing...';
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        if (formType === 'login') {
            // Redirect to main app
            window.location.href = 'index.html';
        } else {
            // Show success message and switch to login
            showSuccessMessage('Account created successfully! Please sign in.');
            document.getElementById('showLogin').click();
        }
        
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }, 2000);
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `
        <div style="
            background: var(--glass-surface);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: var(--space-4);
            margin-bottom: var(--space-4);
            color: #00c851;
            display: flex;
            align-items: center;
            gap: var(--space-2);
            box-shadow: var(--glass-shadow);
        ">
            <span class="material-symbols-rounded">check_circle</span>
            ${message}
        </div>
    `;
    
    const authForm = document.querySelector('.auth-form.active');
    authForm.insertBefore(successDiv, authForm.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

// Scroll Progress Bar
function setupScrollProgress() {
    const progressBar = document.querySelector('.scroll-progress-bar');
    if (!progressBar) return;
    
    function updateScrollProgress() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (scrollTop / scrollHeight) * 100;
        
        progressBar.style.width = `${Math.min(progress, 100)}%`;
    }
    
    window.addEventListener('scroll', updateScrollProgress);
    window.addEventListener('resize', updateScrollProgress);
    
    // Initial call
    updateScrollProgress();
}

// Scroll Reveal Animations
function setupScrollReveal() {
    const revealElements = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right, .scroll-reveal-scale');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Add staggered animation for feature items
                if (entry.target.classList.contains('feature-showcase')) {
                    const featureItems = entry.target.querySelectorAll('.feature-item');
                    featureItems.forEach((item, index) => {
                        setTimeout(() => {
                            item.classList.add('visible');
                        }, index * 100);
                    });
                }
                
                // Add staggered animation for stats
                if (entry.target.classList.contains('stats-grid')) {
                    const statItems = entry.target.querySelectorAll('.stat-item');
                    statItems.forEach((item, index) => {
                        setTimeout(() => {
                            item.classList.add('visible');
                        }, index * 150);
                    });
                }
            }
        });
    }, observerOptions);
    
    revealElements.forEach(element => {
        revealObserver.observe(element);
    });
}

// Scroll Hint
function setupScrollHint() {
    const scrollHint = document.querySelector('.scroll-hint');
    if (!scrollHint) return;
    
    // Hide scroll hint when user scrolls
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 100) {
            scrollHint.style.opacity = '0';
            scrollHint.style.transform = 'translateY(20px)';
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                scrollHint.style.display = 'none';
            }, 300);
        }
    });
    
    // Click to scroll functionality
    scrollHint.addEventListener('click', () => {
        const previewSection = document.querySelector('.auth-preview-section');
        if (previewSection) {
            previewSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        } else {
            // Fallback: scroll down by viewport height
            window.scrollBy({
                top: window.innerHeight * 0.8,
                behavior: 'smooth'
            });
        }
    });
}

// Smooth scrolling for anchor links
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Parallax scrolling for background shapes
function setupParallaxScrolling() {
    const shapes = document.querySelectorAll('.shape');
    
    window.addEventListener('scroll', () => {
        const scrollY = window.pageYOffset;
        
        shapes.forEach((shape, index) => {
            const speed = 0.5 + (index * 0.1);
            const yPos = -(scrollY * speed);
            shape.style.transform = `translateY(${yPos}px)`;
        });
    });
}

// Enhanced scroll behavior for mobile
function setupMobileScrollEnhancements() {
    if ('ontouchstart' in window) {
        // Add momentum scrolling for iOS
        document.body.style.webkitOverflowScrolling = 'touch';
        
        // Prevent bounce scrolling
        document.addEventListener('touchstart', function(e) {
            if (e.touches.length === 1) {
                const scrollY = window.pageYOffset;
                const scrollHeight = document.documentElement.scrollHeight;
                const clientHeight = document.documentElement.clientHeight;
                
                if (scrollY === 0) {
                    window.scrollTo(0, 1);
                } else if (scrollY + clientHeight >= scrollHeight) {
                    window.scrollTo(0, scrollHeight - clientHeight - 1);
                }
            }
        });
    }
}

// Initialize all scroll enhancements
document.addEventListener('DOMContentLoaded', function() {
    setupSmoothScrolling();
    setupParallaxScrolling();
    setupMobileScrollEnhancements();
});

// CSS for spinning animation
const style = document.createElement('style');
style.textContent = `
    .spinning {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);