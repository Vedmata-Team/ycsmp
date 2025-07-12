/**
 * Advanced Animation Library for प्रांतीय युवा प्रकोष्ठ-उत्तर प्रदेश
 * Custom animations and micro-interactions
 */

// Animation constants
const ANIMATION_DURATION = 800;
const STAGGER_DELAY = 100;
const EASING = 'cubic-bezier(0.25, 0.46, 0.45, 0.94)';

/**
 * Initialize all animations when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeScrollAnimations();
    initializeHoverAnimations();
    initializeMicroInteractions();
    initializeParticleEffects();
    initializeTypewriterEffect();
    initializeCountUpAnimations();
    initializeRevealAnimations();
    
    console.log('Advanced animations initialized');
});

/**
 * Scroll-based Animations
 */
function initializeScrollAnimations() {
    // Create intersection observer for scroll animations
    const observerOptions = {
        threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5],
        rootMargin: '0px 0px -100px 0px'
    };
    
    const scrollObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            const element = entry.target;
            const ratio = entry.intersectionRatio;
            
            if (entry.isIntersecting) {
                // Add staggered animations for multiple elements
                if (element.classList.contains('stagger-animation')) {
                    animateStaggeredElements(element);
                }
                
                // Fade in animations
                if (element.classList.contains('fade-in-animation')) {
                    animateFadeIn(element);
                }
                
                // Slide in animations
                if (element.classList.contains('slide-in-animation')) {
                    animateSlideIn(element);
                }
                
                // Scale in animations
                if (element.classList.contains('scale-in-animation')) {
                    animateScaleIn(element);
                }
                
                // Rotate in animations
                if (element.classList.contains('rotate-in-animation')) {
                    animateRotateIn(element);
                }
                
                // Progress bar animations
                if (element.classList.contains('progress-bar-animation')) {
                    animateProgressBar(element, ratio);
                }
                
                // Number counter animations
                if (element.classList.contains('counter-animation')) {
                    animateCounter(element);
                }
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll([
        '.fade-in-animation',
        '.slide-in-animation',
        '.scale-in-animation',
        '.rotate-in-animation',
        '.stagger-animation',
        '.progress-bar-animation',
        '.counter-animation'
    ].join(', '));
    
    animatedElements.forEach(el => {
        scrollObserver.observe(el);
    });
    
    // Parallax scrolling effect
    initializeParallaxScrolling();
}

/**
 * Parallax Scrolling Effects
 */
function initializeParallaxScrolling() {
    const parallaxElements = document.querySelectorAll('.parallax-element');
    
    if (parallaxElements.length === 0) return;
    
    const updateParallax = throttle(() => {
        const scrollTop = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.parallaxSpeed || 0.5;
            const yPos = -(scrollTop * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }, 16);
    
    window.addEventListener('scroll', updateParallax);
}

/**
 * Hover Animations and Micro-interactions
 */
function initializeHoverAnimations() {
    // Card hover effects
    const cards = document.querySelectorAll('.news-card, .event-card, .modern-card, .value-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.15)';
            this.style.transition = 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            
            // Animate child elements
            const cardImage = this.querySelector('.news-image, .event-image');
            if (cardImage) {
                cardImage.style.transform = 'scale(1.05)';
                cardImage.style.transition = 'transform 0.5s ease';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
            
            const cardImage = this.querySelector('.news-image, .event-image');
            if (cardImage) {
                cardImage.style.transform = '';
            }
        });
    });
    
    // Button hover effects
    const buttons = document.querySelectorAll('.btn-modern, .btn-primary-modern, .btn-secondary-modern');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            createRippleEffect(this, event);
        });
    });
    
    // Social link hover effects
    const socialLinks = document.querySelectorAll('.social-link, .hero-social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.1)';
            this.style.transition = 'all 0.3s ease';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

/**
 * Micro-interactions
 */
function initializeMicroInteractions() {
    // Form input focus effects
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
            
            // Create focus ring animation
            const focusRing = document.createElement('div');
            focusRing.className = 'focus-ring';
            this.parentElement.appendChild(focusRing);
            
            setTimeout(() => {
                focusRing.style.transform = 'scale(1)';
                focusRing.style.opacity = '0.3';
            }, 10);
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
            
            const focusRing = this.parentElement.querySelector('.focus-ring');
            if (focusRing) {
                focusRing.style.transform = 'scale(1.2)';
                focusRing.style.opacity = '0';
                setTimeout(() => focusRing.remove(), 300);
            }
        });
    });
    
    // Click ripple effect for buttons
    const clickableElements = document.querySelectorAll('button, .btn, .nav-link');
    
    clickableElements.forEach(element => {
        element.addEventListener('click', function(e) {
            createRippleEffect(this, e);
        });
    });
    
    // Loading spinner animations
    initializeLoadingAnimations();
}

/**
 * Particle Effects
 */
function initializeParticleEffects() {
    // Create floating particles in hero section
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        createFloatingParticles(heroSection);
    }
    
    // Success confetti effect
    window.showConfetti = function() {
        createConfettiEffect();
    };
}

function createFloatingParticles(container) {
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'floating-particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 8 + 4}px;
            height: ${Math.random() * 8 + 4}px;
            background: rgba(253, 133, 53, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${Math.random() * 10 + 10}s infinite linear;
            pointer-events: none;
            z-index: 1;
        `;
        
        container.appendChild(particle);
    }
    
    // Add floating animation keyframes
    if (!document.querySelector('#floating-animation-styles')) {
        const styles = document.createElement('style');
        styles.id = 'floating-animation-styles';
        styles.textContent = `
            @keyframes float {
                0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
}

function createConfettiEffect() {
    const confettiCount = 50;
    const colors = ['#fd8535', '#ffb300', '#28a745', '#dc3545', '#007bff'];
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti-piece';
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}vw;
            top: -10px;
            z-index: 10000;
            animation: confetti-fall ${Math.random() * 3 + 2}s linear forwards;
            transform: rotate(${Math.random() * 360}deg);
        `;
        
        document.body.appendChild(confetti);
        
        setTimeout(() => confetti.remove(), 5000);
    }
    
    // Add confetti animation styles
    if (!document.querySelector('#confetti-animation-styles')) {
        const styles = document.createElement('style');
        styles.id = 'confetti-animation-styles';
        styles.textContent = `
            @keyframes confetti-fall {
                0% { transform: translateY(-100vh) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(720deg); }
            }
        `;
        document.head.appendChild(styles);
    }
}

/**
 * Typewriter Effect
 */
function initializeTypewriterEffect() {
    const typewriterElements = document.querySelectorAll('.typewriter-text');
    
    typewriterElements.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        element.style.borderRight = '2px solid #fd8535';
        
        let index = 0;
        const typeSpeed = 100;
        
        function typeWriter() {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(typeWriter, typeSpeed);
            } else {
                // Blinking cursor effect
                setInterval(() => {
                    element.style.borderRight = element.style.borderRight === 'none' 
                        ? '2px solid #fd8535' 
                        : 'none';
                }, 500);
            }
        }
        
        // Start typewriter when element is visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(typeWriter, 500);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(element);
    });
}

/**
 * Count-up Animations
 */
function initializeCountUpAnimations() {
    const countElements = document.querySelectorAll('.count-up, .stat-number[data-count]');
    
    countElements.forEach(element => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCountUp(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(element);
    });
}

function animateCountUp(element) {
    const target = parseInt(element.getAttribute('data-count') || element.textContent.replace(/\D/g, ''));
    const duration = 20;
    const increment = target / (duration / 5);
    let current = 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        const suffix = element.textContent.includes('+') ? '+' : '';
        element.textContent = Math.floor(current).toLocaleString() + suffix;
    }, 16);
}

/**
 * Reveal Animations
 */
function initializeRevealAnimations() {
    const revealElements = document.querySelectorAll('.reveal-animation');
    
    revealElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(50px)';
        element.style.transition = `all ${ANIMATION_DURATION}ms ${EASING} ${index * STAGGER_DELAY}ms`;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(element);
    });
}

/**
 * Loading Animations
 */
function initializeLoadingAnimations() {
    // Skeleton loading animation
    const skeletonElements = document.querySelectorAll('.skeleton-loading');
    
    skeletonElements.forEach(element => {
        element.style.background = 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)';
        element.style.backgroundSize = '200% 100%';
        element.style.animation = 'skeleton-loading 1.5s infinite';
    });
    
    // Add skeleton loading keyframes
    if (!document.querySelector('#skeleton-loading-styles')) {
        const styles = document.createElement('style');
        styles.id = 'skeleton-loading-styles';
        styles.textContent = `
            @keyframes skeleton-loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
        `;
        document.head.appendChild(styles);
    }
}

/**
 * Individual Animation Functions
 */
function animateFadeIn(element) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${ANIMATION_DURATION}ms ${EASING}`;
    
    setTimeout(() => {
        element.style.opacity = '1';
    }, 100);
}

function animateSlideIn(element) {
    const direction = element.dataset.slideDirection || 'up';
    let transform = '';
    
    switch(direction) {
        case 'up': transform = 'translateY(50px)'; break;
        case 'down': transform = 'translateY(-50px)'; break;
        case 'left': transform = 'translateX(50px)'; break;
        case 'right': transform = 'translateX(-50px)'; break;
    }
    
    element.style.transform = transform;
    element.style.opacity = '0';
    element.style.transition = `all ${ANIMATION_DURATION}ms ${EASING}`;
    
    setTimeout(() => {
        element.style.transform = 'translateY(0) translateX(0)';
        element.style.opacity = '1';
    }, 100);
}

function animateScaleIn(element) {
    element.style.transform = 'scale(0.8)';
    element.style.opacity = '0';
    element.style.transition = `all ${ANIMATION_DURATION}ms ${EASING}`;
    
    setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.opacity = '1';
    }, 100);
}

function animateRotateIn(element) {
    element.style.transform = 'rotate(-180deg) scale(0.5)';
    element.style.opacity = '0';
    element.style.transition = `all ${ANIMATION_DURATION}ms ${EASING}`;
    
    setTimeout(() => {
        element.style.transform = 'rotate(0deg) scale(1)';
        element.style.opacity = '1';
    }, 100);
}

function animateStaggeredElements(container) {
    const children = container.children;
    
    Array.from(children).forEach((child, index) => {
        child.style.opacity = '0';
        child.style.transform = 'translateY(30px)';
        child.style.transition = `all ${ANIMATION_DURATION}ms ${EASING}`;
        
        setTimeout(() => {
            child.style.opacity = '1';
            child.style.transform = 'translateY(0)';
        }, index * STAGGER_DELAY);
    });
}

function animateProgressBar(element, ratio) {
    const targetWidth = element.style.width || element.getAttribute('data-width') || '100%';
    const currentWidth = parseInt(targetWidth) * ratio;
    
    element.style.width = currentWidth + '%';
    element.style.transition = `width 0.3s ease`;
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-count') || element.textContent);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + (element.textContent.includes('+') ? '+' : '');
    }, 16);
}

/**
 * Ripple Effect
 */
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    // Add ripple animation
    if (!document.querySelector('#ripple-animation-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ripple-animation-styles';
        styles.textContent = `
            @keyframes ripple {
                to { transform: scale(2); opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    setTimeout(() => ripple.remove(), 600);
}

/**
 * Utility function for throttling
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export animation functions for global access
window.PyupAnimations = {
    animateFadeIn,
    animateSlideIn,
    animateScaleIn,
    animateRotateIn,
    animateStaggeredElements,
    animateCountUp,
    createRippleEffect,
    createConfettiEffect,
    showConfetti: () => createConfettiEffect()
};
