// Vehicle Pass Download Handler with Loading States
class VehiclePassDownloader {
    constructor() {
        this.isDownloading = false;
        this.init();
    }

    init() {
        // Find all vehicle pass download links
        document.addEventListener('DOMContentLoaded', () => {
            this.attachDownloadHandlers();
        });
    }

    attachDownloadHandlers() {
        // Select all vehicle pass download links
        const vehiclePassLinks = document.querySelectorAll('a[href*="/vehicle-pass/generate/"]');
        
        vehiclePassLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleDownload(link);
            });
        });
    }

    async handleDownload(link) {
        if (this.isDownloading) {
            return;
        }

        this.isDownloading = true;
        const originalContent = link.innerHTML;
        const downloadUrl = link.href;

        try {
            // Show loading state
            this.showLoadingState(link);
            
            // Create loading overlay
            this.createLoadingOverlay();
            
            // Start download and progress together
            const downloadPromise = this.downloadFile(downloadUrl, link);
            await this.simulateDownloadProcess(downloadPromise);
            
        } catch (error) {
            this.showError('वाहन पास जेनरेट करने में त्रुटि हुई। कृपया पुनः प्रयास करें।');
        } finally {
            // Restore original state
            link.innerHTML = originalContent;
            this.removeLoadingOverlay();
            this.isDownloading = false;
        }
    }

    showLoadingState(link) {
        link.innerHTML = '<i class="bi bi-hourglass-split"></i> जेनरेट हो रहा है...';
        link.style.pointerEvents = 'none';
        link.style.opacity = '0.7';
    }

    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'vehiclePassLoadingOverlay';
        overlay.innerHTML = `
            <div class="loading-overlay" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                font-family: 'Kalam', cursive;
            ">
                <div class="loading-content" style="
                    background: white;
                    padding: 2rem;
                    border-radius: 15px;
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                ">
                    <div class="spinner" style="
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #dc3545;
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 1rem;
                    "></div>
                    <h5 style="color: #333; margin-bottom: 1rem;">🚗 वाहन पास तैयार हो रहा है</h5>
                    <div class="progress-bar" style="
                        width: 100%;
                        height: 8px;
                        background: #f0f0f0;
                        border-radius: 4px;
                        overflow: hidden;
                        margin: 1rem 0;
                    ">
                        <div class="progress-fill" id="vehiclePassProgress" style="
                            height: 100%;
                            background: linear-gradient(90deg, #dc3545, #c82333);
                            border-radius: 4px;
                            width: 0%;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <div id="vehiclePassStatus" style="color: #666; font-size: 0.9rem;">
                        टेम्प्लेट लोड हो रहा है...
                    </div>
                    <div id="vehiclePassPercent" style="color: #dc3545; font-weight: bold; margin-top: 0.5rem;">
                        0%
                    </div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(overlay);
    }

    async simulateDownloadProcess(downloadPromise) {
        const statusMessages = [
            'टेम्प्लेट लोड हो रहा है...',
            'वाहन जानकारी प्राप्त कर रहे हैं...',
            'QR कोड जेनरेट हो रहा है...',
            'बैकग्राउंड इमेज लोड हो रहा है...',
            'HTML रेंडर हो रहा है...',
            'इमेज में कन्वर्ट हो रहा है...',
            'फाइनल प्रोसेसिंग...'
        ];

        let progress = 0;
        let downloadComplete = false;
        const progressElement = document.getElementById('vehiclePassProgress');
        const statusElement = document.getElementById('vehiclePassStatus');
        const percentElement = document.getElementById('vehiclePassPercent');

        // Monitor download completion
        downloadPromise.then(() => {
            downloadComplete = true;
            // Immediately show 100% when server responds
            if (progressElement) progressElement.style.width = '100%';
            if (percentElement) percentElement.textContent = '100%';
            if (statusElement) statusElement.textContent = 'डाउनलोड शुरू हो रहा है...';
        });

        // Animate progress up to 95% while waiting for server
        for (let i = 0; i < statusMessages.length && !downloadComplete; i++) {
            if (statusElement) statusElement.textContent = statusMessages[i];
            
            const targetProgress = ((i + 1) / statusMessages.length) * 95; // Only go to 95%
            
            while (progress < targetProgress && !downloadComplete) {
                progress += 15;
                if (progress > targetProgress) progress = targetProgress;
                
                if (progressElement) progressElement.style.width = progress + '%';
                if (percentElement) percentElement.textContent = Math.round(progress) + '%';
                
                await this.delay(30);
            }
            
            if (!downloadComplete) await this.delay(80);
        }

        // Wait for download to complete
        await downloadPromise;
    }

    async downloadFile(url, linkElement) {
        return new Promise((resolve, reject) => {
            fetch(url)
                .then(response => {
                    if (response.ok) {
                        // Server responded - show 100% immediately
                        const progressElement = document.getElementById('vehiclePassProgress');
                        const percentElement = document.getElementById('vehiclePassPercent');
                        const statusElement = document.getElementById('vehiclePassStatus');
                        
                        if (progressElement) progressElement.style.width = '100%';
                        if (percentElement) percentElement.textContent = '100%';
                        if (statusElement) statusElement.textContent = 'डाउनलोड शुरू हो रहा है...';
                        
                        // Trigger download
                        const tempLink = document.createElement('a');
                        tempLink.href = url;
                        tempLink.style.display = 'none';
                        tempLink.download = `vehicle_pass_${Date.now()}.png`;
                        
                        document.body.appendChild(tempLink);
                        tempLink.click();
                        document.body.removeChild(tempLink);
                        
                        this.showSuccess('वाहन पास सफलतापूर्वक डाउनलोड हो गया!');
                        resolve();
                    } else {
                        reject(new Error('Download failed'));
                    }
                })
                .catch(error => reject(error));
        });
    }

    removeLoadingOverlay() {
        const overlay = document.getElementById('vehiclePassLoadingOverlay');
        if (overlay) {
            overlay.remove();
        }
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

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the downloader
new VehiclePassDownloader();