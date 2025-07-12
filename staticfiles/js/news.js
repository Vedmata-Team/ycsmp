// News functionality JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Like button functionality
    const likeButtons = document.querySelectorAll('.like-btn, .btn-like-article');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.dataset.newsId;
            const icon = this.querySelector('i');
            const countElement = document.getElementById('likes-count') || this.querySelector('span');
            const isLiked = this.classList.contains('liked');
            const action = isLiked ? 'dislike' : 'like';
            
            // Send AJAX request
            fetch(`/news/${newsId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `action=${action}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update UI based on server response
                    if (data.action === 'like') {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        this.classList.add('liked');
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        this.classList.remove('liked');
                    }
                    
                    // Update count from server
                    if (countElement) {
                        countElement.textContent = data.likes_count;
                    }
                    
                    // Update stats display if exists
                    const statsElement = document.querySelector('.stat-item i.bi-heart-fill')?.parentElement;
                    if (statsElement) {
                        statsElement.innerHTML = `<i class="bi bi-heart-fill"></i> ${data.likes_count}`;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('कुछ गलत हुआ, कृपया पुनः प्रयास करें', 'error');
            });
        });
    });

    // Share button functionality
    const shareButtons = document.querySelectorAll('.share-btn, .btn-share-article');
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const title = this.dataset.title || document.title;
            const newsUrl = this.dataset.url;
            const fullUrl = newsUrl ? window.location.origin + newsUrl : window.location.href;
            
            if (navigator.share) {
                navigator.share({
                    title: title,
                    url: fullUrl
                });
            } else {
                navigator.clipboard.writeText(fullUrl).then(() => {
                    showToast('लिंक कॉपी हो गया!');
                });
            }
        });
    });

    // Bookmark button functionality
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark-article');
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            
            if (icon.classList.contains('bi-bookmark')) {
                icon.classList.remove('bi-bookmark');
                icon.classList.add('bi-bookmark-fill');
                showToast('बुकमार्क में जोड़ा गया!');
            } else {
                icon.classList.remove('bi-bookmark-fill');
                icon.classList.add('bi-bookmark');
                showToast('बुकमार्क से हटाया गया!');
            }
        });
    });

    // Print button functionality
    const printButtons = document.querySelectorAll('.btn-print-article');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
});

// Social media sharing functions
function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400');
}

function shareOnTwitter() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', 'width=600,height=400');
}

function shareOnWhatsApp() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(`${document.title} - ${window.location.href}`);
    window.open(`https://wa.me/?text=${text}`, '_blank');
}

function shareOnTelegram() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://t.me/share/url?url=${url}&text=${text}`, '_blank');
}

function shareOnLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank', 'width=600,height=400');
}

// Toast notification function
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi bi-check-circle-fill"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Filter functionality for news list
function initializeFilters() {
    const searchInput = document.querySelector('.search-input');
    const filterSelects = document.querySelectorAll('.filter-select');
    
    if (searchInput) {
        // Only submit on Enter key press
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.form.submit();
            }
        });
        
        // Visual feedback for search input
        searchInput.addEventListener('input', function() {
            const searchBtn = document.querySelector('.search-btn');
            if (this.value.length > 0) {
                searchBtn.classList.add('active');
            } else {
                searchBtn.classList.remove('active');
            }
        });
    }
    
    // Submit form when filter selection changes
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            if (this.value !== this.defaultValue) {
                this.form.submit();
            }
        });
    });
}

// Initialize filters if on news list page
if (document.querySelector('.filters-section')) {
    initializeFilters();
}