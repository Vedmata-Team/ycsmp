/**
 * Universal Date of Birth Verification System
 * Works for ID card download, vehicle pass download, and all previews
 */

class DOBVerification {
    constructor() {
        this.userDOB = null; // Expected DOB from server
        this.isVerified = false;
        this.init();
    }

    init() {
        // Get DOB from data attribute or global variable
        this.userDOB = window.USER_DOB || document.body.dataset.userDob;
        this.setupEventListeners();
        this.blurDOBElements();
    }

    setupEventListeners() {
        this.interceptDownloadLinks();
        
        document.addEventListener('change', (e) => {
            if (e.target.id === 'dobInput') {
                const inputDOB = e.target.value;
                if (inputDOB && this.validateDOBFormat(inputDOB)) {
                    const modal = e.target.closest('.dob-verification-modal');
                    const downloadUrl = modal.dataset.downloadUrl;
                    this.isVerified = true;
                    this.closeModal(modal);
                    this.unblurDOBElements();
                    this.instantDownload(downloadUrl);
                }
            }
        });
    }
    
    interceptDownloadLinks() {
        const downloadLinks = document.querySelectorAll('.download-protected, .download-btn, .btn-success');
        downloadLinks.forEach(link => {
            const originalUrl = link.href || link.dataset.downloadUrl;
            
            // Remove original href to prevent direct access
            link.removeAttribute('href');
            link.style.cursor = 'pointer';
            
            // Add click handler
            link.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.showVerificationModal(originalUrl);
            });
        });
    }

    blurDOBElements() {
        // Blur DOB in previews and profiles
        const dobElements = document.querySelectorAll('[data-dob], .dob-field, .date-of-birth');
        dobElements.forEach(element => {
            if (!this.isVerified) {
                element.style.filter = 'blur(4px)';
                element.style.userSelect = 'none';
                element.title = 'Verify your identity to view';
            }
        });
    }

    showVerificationModal(downloadUrl) {
        const modal = this.createModal(downloadUrl);
        modal.dataset.downloadUrl = downloadUrl;
        document.body.appendChild(modal);
        modal.style.display = 'flex';
        
        modal.querySelector('#dobInput').focus();
    }

    createModal(downloadUrl) {
        const modal = document.createElement('div');
        modal.className = 'dob-verification-modal';
        modal.innerHTML = `
            <div class="dob-modal-content">
                <div class="dob-modal-header">
                    <i class="bi bi-shield-check"></i>
                    <h3>Identity Verification</h3>
                    <button class="dob-close-btn">&times;</button>
                </div>
                <div class="dob-modal-body">
                    <p>Please enter your Date of Birth to proceed with download</p>
                    <div class="dob-input-group">
                        <label for="dobInput">Date of Birth</label>
                        <input type="date" id="dobInput" class="dob-input" required>
                        <small>Enter the date of birth used during registration</small>
                    </div>
                    <div class="dob-error-message" style="display: none;">
                        <i class="bi bi-exclamation-triangle"></i>
                        Incorrect date of birth. Please try again.
                    </div>
                </div>
                <div class="dob-modal-footer">
                    <button class="dob-cancel-btn">Cancel</button>
                    <button class="dob-verify-btn">Verify & Download</button>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.dob-close-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.closeModal(modal);
        });
        modal.querySelector('.dob-cancel-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.closeModal(modal);
        });
        modal.querySelector('.dob-verify-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.verifyDOB(modal, downloadUrl);
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal(modal);
        });

        // Handle Enter key
        modal.querySelector('#dobInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.verifyDOB(modal, downloadUrl);
            }
        });

        return modal;
    }

    verifyDOB(modal, downloadUrl) {
        const inputDOB = modal.querySelector('#dobInput').value;
        const errorDiv = modal.querySelector('.dob-error-message');
        
        if (!inputDOB) {
            this.showError(errorDiv, 'Please enter your date of birth');
            return;
        }

        if (this.validateDOBFormat(inputDOB)) {
            this.isVerified = true;
            this.closeModal(modal);
            this.unblurDOBElements();
            this.instantDownload(downloadUrl);
        } else {
            this.showError(errorDiv, 'Incorrect date of birth. Please try again.');
            modal.querySelector('#dobInput').value = '';
            modal.querySelector('#dobInput').focus();
        }
    }

    showError(errorDiv, message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 3000);
    }

    unblurDOBElements() {
        const dobElements = document.querySelectorAll('[data-dob], .dob-field, .date-of-birth');
        dobElements.forEach(element => {
            element.style.filter = 'none';
            element.style.userSelect = 'auto';
            element.title = '';
        });
    }

    validateDOBFormat(inputDOB) {
        const inputFormatted = inputDOB;
        let userFormatted = this.userDOB;
        
        if (this.userDOB && this.userDOB.includes('/')) {
            const parts = this.userDOB.split('/');
            if (parts.length === 3) {
                userFormatted = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
            }
        } else if (this.userDOB && !this.userDOB.includes('-')) {
            try {
                userFormatted = new Date(this.userDOB).toISOString().split('T')[0];
            } catch (e) {
                console.error('Date parsing error:', e);
            }
        }
        
        if (inputFormatted === userFormatted) return true;
        
        try {
            const inputDate = new Date(inputFormatted);
            const userDate = new Date(userFormatted);
            if (inputDate.getTime() === userDate.getTime()) return true;
        } catch (e) {}
        
        const inputParts = inputFormatted.split('-');
        const userParts = userFormatted.split('-');
        if (inputParts.length === 3 && userParts.length === 3) {
            return inputParts[0] === userParts[0] && 
                   inputParts[1] === userParts[1] && 
                   inputParts[2] === userParts[2];
        }
        
        return false;
    }
    
    instantDownload(downloadUrl) {
        const tempLink = document.createElement('a');
        tempLink.href = downloadUrl;
        tempLink.style.display = 'none';
        tempLink.download = '';
        
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
        
        this.showSuccessMessage();
    }

    showSuccessMessage() {
        const toast = document.createElement('div');
        toast.className = 'dob-success-toast';
        toast.innerHTML = `
            <i class="bi bi-check-circle"></i>
            <span>Verification successful! Starting download...</span>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    closeModal(modal) {
        modal.remove();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DOBVerification();
});

// CSS Styles
const dobStyles = `
<style>
.dob-verification-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    font-family: 'Inter', sans-serif;
}

.dob-modal-content {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    animation: dobModalSlide 0.3s ease-out;
}

@keyframes dobModalSlide {
    from { transform: translateY(-50px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.dob-modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
}

.dob-modal-header i {
    color: #28a745;
    font-size: 1.2rem;
}

.dob-modal-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.1rem;
    font-weight: 600;
}

.dob-close-btn {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #6c757d;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.dob-modal-body {
    padding: 1.5rem;
}

.dob-modal-body p {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 0.9rem;
}

.dob-input-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #495057;
    font-weight: 500;
    font-size: 0.9rem;
}

.dob-input {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s ease;
}

.dob-input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.dob-input-group small {
    display: block;
    margin-top: 0.5rem;
    color: #6c757d;
    font-size: 0.8rem;
}

.dob-error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 6px;
    margin-top: 1rem;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dob-modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e9ecef;
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
}

.dob-cancel-btn, .dob-verify-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.dob-cancel-btn {
    background: #6c757d;
    color: white;
}

.dob-cancel-btn:hover {
    background: #5a6268;
}

.dob-verify-btn {
    background: #007bff;
    color: white;
}

.dob-verify-btn:hover {
    background: #0056b3;
}

.dob-success-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #d4edda;
    color: #155724;
    padding: 1rem 1.5rem;
    border-radius: 6px;
    border: 1px solid #c3e6cb;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    z-index: 10001;
    animation: dobToastSlide 0.3s ease-out;
}

@keyframes dobToastSlide {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

@media (max-width: 480px) {
    .dob-modal-content {
        width: 95%;
        margin: 1rem;
    }
    
    .dob-modal-footer {
        flex-direction: column;
    }
    
    .dob-cancel-btn, .dob-verify-btn {
        width: 100%;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', dobStyles);