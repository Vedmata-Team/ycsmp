/**
 * Main JavaScript file for प्रांतीय युवा प्रकोष्ठ-उत्तर प्रदेश
 * Enhanced functionality for modern UI/UX
 */

// Global variables
let isScrolling = false;
let lastScrollTop = 0;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeScrollEffects();
    initializeBackToTop();
    initializeReadingProgress();
    initializeFormValidation();
    initializeTooltips();
    initializeDropdowns();
    initializeModals();
    initializeLazyLoading();
    initializeSearch();
    initializeThemeToggle();
    
    // Initialize jQuery-dependent features if available
    if (typeof $ !== 'undefined') {
        initializejQueryFeatures();
    }
    
    console.log('प्रांतीय युवा प्रकोष्ठ website initialized successfully');
});

/**
 * Navigation Enhancement
 */
function initializeNavigation() {
    const navbar = document.querySelector('.main-header');
    const navbarToggler = document.querySelector('.custom-toggler');
    const navbarCollapse = document.getElementById('mainNavbar');
    const navLinks = document.querySelectorAll('.modern-nav-link');

    // Sticky navbar with scroll effects
    window.addEventListener('scroll', function() {
        if (!isScrolling) {
            window.requestAnimationFrame(function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (navbar) {
                    if (scrollTop > 100) {
                        navbar.classList.add('navbar-scrolled');
                        navbar.style.background = 'rgba(255, 248, 225, 0.95)';
                        navbar.style.backdropFilter = 'blur(10px)';
                        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
                    } else {
                        navbar.classList.remove('navbar-scrolled');
                        navbar.style.background = '';
                        navbar.style.backdropFilter = '';
                        navbar.style.boxShadow = '';
                    }
                }
                lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
                isScrolling = false;
            });
        }
        isScrolling = true;
    });

    // Enhanced mobile menu toggle
    if (navbarToggler && navbarCollapse) {
        // Only toggle 'active' class on the button, let Bootstrap handle menu
        navbarCollapse.addEventListener('show.bs.collapse', function () {
            navbarToggler.classList.add('active');
        });
        navbarCollapse.addEventListener('hide.bs.collapse', function () {
            navbarToggler.classList.remove('active');
        });
    }

    // Smooth scroll for anchor links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
            // Close mobile menu after click (Bootstrap way)
            if (window.innerWidth < 992 && navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
                bsCollapse.hide();
            }
        });
    });

    // Active nav link highlighting
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Scroll Effects and Animations
 */
function initializeScrollEffects() {
    // Parallax effect for hero sections
    const heroSections = document.querySelectorAll('.hero-section');
    
    window.addEventListener('scroll', function() {
        if (!isScrolling) {
            window.requestAnimationFrame(function() {
                const scrolled = window.pageYOffset;
                
                heroSections.forEach(hero => {
                    const rate = scrolled * -0.5;
                    const yPos = Math.round(rate);
                    hero.style.transform = `translate3d(0, ${yPos}px, 0)`;
                });
                
                isScrolling = false;
            });
        }
        isScrolling = true;
    });
    
    // Reveal animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Counter animation for statistics
                if (entry.target.classList.contains('stat-number')) {
                    animateCounter(entry.target);
                }
                
                // Progress bar animation
                if (entry.target.classList.contains('progress-fill')) {
                    animateProgressBar(entry.target);
                }
            }
        });
    }, observerOptions);
    
    // Observe elements for scroll animations
    const animatedElements = document.querySelectorAll([
        '.news-card',
        '.event-card',
        '.stat-card',
        '.value-card',
        '.work-area-card',
        '.team-card',
        '.stat-number',
        '.progress-fill'
    ].join(', '));
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Back to Top Button
 */
function initializeBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Reading Progress Bar
 */
function initializeReadingProgress() {
    const progressBar = document.getElementById('reading-progress');
    
    if (progressBar) {
        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }
}

/**
 * Enhanced Form Validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Show validation errors with smooth animations
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    field.addEventListener('input', function() {
                        if (this.checkValidity()) {
                            this.classList.remove('is-invalid');
                            this.classList.add('is-valid');
                        }
                    });
                });
                
                // Focus first invalid field
                if (invalidFields.length > 0) {
                    invalidFields[0].focus();
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

/**
 * Modern Tooltips
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip(this);
        });
    });
}

function showTooltip(element) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = element.getAttribute('data-tooltip');
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    tooltip.classList.add('show');
    element._tooltip = tooltip;
}

function hideTooltip(element) {
    if (element._tooltip) {
        element._tooltip.remove();
        element._tooltip = null;
    }
}

/**
 * Enhanced Dropdowns
 */
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-modern');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle-modern');
        const menu = dropdown.querySelector('.dropdown-menu-modern');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                dropdown.classList.toggle('active');
            });
        }
    });
    
    // Enable auto-close on outside click
    document.addEventListener('click', function(e) {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    });
}

/**
 * Modal Enhancement
 */
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    // Close modal handlers
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal') || e.target.classList.contains('modal-close')) {
            hideModal(e.target.closest('.modal'));
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                hideModal(openModal);
            }
        }
    });
}

function showModal(modal) {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Focus trap
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusableElements.length > 0) {
        focusableElements[0].focus();
    }
}

function hideModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

/**
 * Lazy Loading for Images
 */
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        imageObserver.observe(img);
    });
}

/**
 * Enhanced Search Functionality
 */
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase();
            
            if (searchTerm.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(searchTerm, this);
                }, 300);
            }
        });
    });
}

function performSearch(term, inputElement) {
    // This would typically make an AJAX call to the server
    // For now, we'll just add visual feedback
    const searchButton = inputElement.parentElement.querySelector('.search-btn');
    if (searchButton) {
        searchButton.classList.add('active');
        setTimeout(() => {
            searchButton.classList.remove('active');
        }, 1000);
    }
}

/**
 * Theme Toggle (Light/Dark mode preparation)
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            
            // Save preference
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('darkTheme', isDark);
        });
        
        // Load saved theme preference
        const savedTheme = localStorage.getItem('darkTheme');
        if (savedTheme === 'true') {
            document.body.classList.add('dark-theme');
        }
    }
}

/**
 * Counter Animation
 */
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
        element.textContent = Math.floor(current) + '+';
    }, 16);
}

/**
 * Progress Bar Animation
 */
function animateProgressBar(element) {
    const targetWidth = element.style.width || element.getAttribute('data-width') || '0%';
    element.style.width = '0%';
    
    setTimeout(() => {
        element.style.width = targetWidth;
    }, 100);
}

/**
 * jQuery-dependent Features
 */
function initializejQueryFeatures() {
    // Enhanced form submission with loading states
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"], input[type="submit"]');
        const originalText = submitBtn.html() || submitBtn.val();
        
        if (!submitBtn.hasClass('loading')) {
            submitBtn.addClass('loading');
            
            if (submitBtn.is('button')) {
                submitBtn.html('<i class="bi bi-hourglass-split me-2"></i>Loading...');
            } else {
                submitBtn.val('Loading...');
            }
            
            // Reset after 5 seconds (fallback)
            setTimeout(() => {
                submitBtn.removeClass('loading');
                if (submitBtn.is('button')) {
                    submitBtn.html(originalText);
                } else {
                    submitBtn.val(originalText);
                }
            }, 5000);
        }
    });
    
    // AJAX form handling
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action') || window.location.href;
        const method = form.attr('method') || 'POST';
        const data = form.serialize();
        
        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(response) {
                showNotification('Success!', 'success');
                if (response.redirect) {
                    window.location.href = response.redirect;
                }
            },
            error: function() {
                showNotification('An error occurred. Please try again.', 'error');
            }
        });
    });
    
    // Enhanced hover effects for cards
    $('.news-card, .event-card, .modern-card').hover(
        function() {
            $(this).addClass('hover-effect');
        },
        function() {
            $(this).removeClass('hover-effect');
        }
    );
    
    // Smooth scrolling for internal links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 800);
        }
    });
}

/**
 * Notification System
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi bi-${getNotificationIcon(type)} me-2"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle-fill';
        case 'error': return 'exclamation-triangle-fill';
        case 'warning': return 'info-circle-fill';
        default: return 'info-circle-fill';
    }
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

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

// Performance monitoring
function measurePerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                    console.log('DOM ready time:', perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart, 'ms');
                }
            }, 0);
        });
    }
}

// Initialize performance monitoring
measurePerformance();

// Export functions for global access
window.PyupUtils = {
    showNotification,
    animateCounter,
    animateProgressBar,
    showModal,
    hideModal,
    debounce,
    throttle
};
