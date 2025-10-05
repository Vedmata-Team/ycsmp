// Vehicle Pass Download Handler with Loading States
if (typeof VehiclePassDownloader === 'undefined') {
class VehiclePassDownloader {
    constructor() {
        this.isDownloading = false;
        this.isVerified = false;
        this.userDOB = window.USER_DOB || '1995-12-04';
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.attachDownloadHandlers();
            });
        } else {
            this.attachDownloadHandlers();
        }
    }

    attachDownloadHandlers() {
        // Select all protected links (download, preview, review)
        const protectedLinks = document.querySelectorAll('a[href*="/vehicle-pass/generate/"], a[href*="/id/card/"], a[href*="/vehicle-pass/preview/"], a[href*="/id-card/preview/"], a[href*="/id/preview/"], a[href*="/review/"], .download-btn, .btn-success, .preview-btn, .review-btn, .id-card-btn, .download-protected');
        
        protectedLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleAccess(link);
            });
        });
    }

    async handleAccess(link) {
        if (this.isDownloading) {
            return;
        }

        // Check DOB verification first
        if (!this.isVerified) {
            this.showDOBVerification(link);
            return;
        }

        this.proceedWithAccess(link);
    }
    
    proceedWithAccess(link) {
        const url = link.href || link.dataset.downloadUrl;
        
        // Check if it's DOB viewing
        if (url === '#view-dob') {
            this.showDOB(link);
        } else if (url.includes('/generate/') || link.classList.contains('download-btn')) {
            this.instantDownload(link);
        } else {
            // Navigate to preview/review page
            window.location.href = url;
        }
    }
    
    showDOB(link) {
        // Find the DOB field and unblur it
        const dobField = document.querySelector('.dob-field');
        if (dobField) {
            dobField.innerHTML = dobField.querySelector('span').textContent.replace(/•/g, '');
            dobField.style.cursor = 'default';
            dobField.title = 'Verified';
            dobField.style.color = '#28a745';
            dobField.style.fontWeight = '600';
            dobField.style.background = '#d4edda';
            dobField.style.border = '1px solid #28a745';
            
            this.showSuccess('Date of birth verified successfully!');
        }
    }

    validateDOB(inputDOB) {
        if (!this.userDOB) {
            console.log('No USER_DOB set - using test date 1995-12-04');
            this.userDOB = '1995-12-04'; // Set test DOB
        }
        
        const inputFormatted = inputDOB;
        let userFormatted = this.userDOB;
        
        if (this.userDOB.includes('/')) {
            const parts = this.userDOB.split('/');
            if (parts.length === 3) {
                userFormatted = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
            }
        } else if (!this.userDOB.includes('-')) {
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
        const userParts = userFormatted ? userFormatted.split('-') : [];
        if (inputParts.length === 3 && userParts.length === 3) {
            return inputParts[0] === userParts[0] && 
                   inputParts[1] === userParts[1] && 
                   inputParts[2] === userParts[2];
        }
        
        return false;
    }
    
    instantDownload(link) {
        console.log('Starting instant download');
        const downloadUrl = link.href;
        console.log('Download URL:', downloadUrl);
        
        // Direct download without any loading states
        const tempLink = document.createElement('a');
        tempLink.href = downloadUrl;
        tempLink.style.display = 'none';
        tempLink.download = `vehicle_pass_${Date.now()}.png`;
        
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
        
        console.log('Download triggered');
        this.showSuccess('वाहन पास सफलतापूर्वक डाउनलोड हो गया!');
    }

    showSuccess(message) {
        const toast = document.createElement('div');
        toast.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                z-index: 10000;
                font-family: 'Kalam', cursive;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                animation: slideIn 0.3s ease;
            ">
                <i class="bi bi-check-circle-fill"></i> ${message}
            </div>
            <style>
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            </style>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 2000);
    }

    showError(message) {
        const toast = document.createElement('div');
        toast.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #dc3545;
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                z-index: 10000;
                font-family: 'Kalam', cursive;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            ">
                <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            </div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showDOBVerification(link) {
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                font-family: 'Inter', sans-serif;
            ">
                <div style="
                    background: white;
                    border-radius: 12px;
                    width: 90%;
                    max-width: 400px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    animation: modalSlide 0.3s ease-out;
                ">
                    <div style="
                        padding: 1.5rem;
                        border-bottom: 1px solid #e9ecef;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        position: relative;
                    ">
                        <i class="bi bi-shield-check" style="color: #28a745; font-size: 1.2rem;"></i>
                        <h3 style="margin: 0; color: #2c3e50; font-size: 1.1rem; font-weight: 600;">Identity Verification</h3>
                        <button onclick="window.location.reload()" style="
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
                        ">&times;</button>
                    </div>
                    <div style="padding: 1.5rem;">
                        <p style="margin: 0 0 1rem 0; color: #495057; font-size: 0.9rem;">
                            Please enter your Date of Birth to proceed with download
                        </p>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; color: #495057; font-weight: 500; font-size: 0.9rem;">
                                Date of Birth
                            </label>
                            <input type="date" id="dobInput" style="
                                width: 100%;
                                padding: 0.75rem;
                                border: 2px solid #e9ecef;
                                border-radius: 6px;
                                font-size: 1rem;
                                transition: border-color 0.2s ease;
                            " required>
                            <small style="display: block; margin-top: 0.5rem; color: #6c757d; font-size: 0.8rem;">
                                Enter the date of birth used during registration
                            </small>
                        </div>
                        <div id="dobError" style="
                            background: #f8d7da;
                            color: #721c24;
                            padding: 0.75rem;
                            border-radius: 6px;
                            margin-top: 1rem;
                            font-size: 0.9rem;
                            display: none;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            <i class="bi bi-exclamation-triangle"></i>
                            <span>Incorrect date of birth. Please try again.</span>
                        </div>
                    </div>
                    <div style="
                        padding: 1rem 1.5rem;
                        border-top: 1px solid #e9ecef;
                        display: flex;
                        gap: 0.5rem;
                        justify-content: flex-end;
                    ">
                        <button onclick="window.location.reload()" style="
                            padding: 0.6rem 1.2rem;
                            border: none;
                            border-radius: 6px;
                            font-size: 0.9rem;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s ease;
                            background: #6c757d;
                            color: white;
                        ">Cancel</button>
                        <button id="verifyDOB" type="button" style="
                            padding: 0.6rem 1.2rem;
                            border: none;
                            border-radius: 6px;
                            font-size: 0.9rem;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s ease;
                            background: #007bff;
                            color: white;
                            user-select: none;
                        " onmousedown="this.style.background='#0056b3'" onmouseup="this.style.background='#007bff'">Verify & Download</button>
                    </div>
                </div>
            </div>
            <style>
                @keyframes modalSlide {
                    from { transform: translateY(-50px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            </style>
        `;
        
        document.body.appendChild(modal);
        
        const dobInput = modal.querySelector('#dobInput');
        const verifyBtn = modal.querySelector('#verifyDOB');
        const errorDiv = modal.querySelector('#dobError');
        
        dobInput.focus();
        
        // Removed auto-verification - only verify on button click
        
        const verifyDOB = () => {
            console.log('Verify button clicked');
            const inputDOB = dobInput.value;
            console.log('Input DOB:', inputDOB);
            console.log('User DOB:', this.userDOB);
            
            if (!inputDOB) {
                console.log('No DOB entered');
                this.showDOBError(errorDiv, 'Please enter your date of birth');
                return;
            }
            
            const isValid = this.validateDOB(inputDOB);
            console.log('DOB validation result:', isValid);
            
            if (isValid) {
                console.log('DOB valid - proceeding with download');
                this.isVerified = true;
                modal.remove();
                this.proceedWithAccess(link);
            } else {
                console.log('DOB invalid - showing error');
                this.showDOBError(errorDiv, 'Incorrect date of birth. Please try again.');
                dobInput.value = '';
                dobInput.focus();
            }
        };
        
        verifyBtn.addEventListener('click', (e) => {
            console.log('Verify button event triggered');
            e.preventDefault();
            e.stopPropagation();
            verifyDOB();
        });
        
        dobInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                verifyDOB();
            }
        });
    }
    
    showDOBError(errorDiv, message) {
        errorDiv.querySelector('span').textContent = message;
        errorDiv.style.display = 'flex';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 3000);
    }


}

// Initialize the downloader
if (typeof window.vehiclePassDownloader === 'undefined') {
    window.vehiclePassDownloader = new VehiclePassDownloader();
}
}