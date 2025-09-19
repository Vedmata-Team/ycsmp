// Document Upload with Cropping and Compression
class DocumentUploader {
    constructor() {
        this.cropper = null;
        this.currentFile = null;
        this.currentFieldName = null;
        this.maxFileSize = 200 * 1024; // 200KB
        this.cameraStream = null;
        this.currentFacingMode = 'environment'; // Default to back camera
        this.initializeUploader();
    }

    initializeUploader() {
        // Create modal HTML
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        const modalHTML = `
        <div class="modal fade" id="documentUploadModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">दस्तावेज़ अपलोड करें</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Upload Options -->
                        <div id="uploadOptions" class="text-center mb-4">
                            <h6>फोटो कैसे अपलोड करना चाहते हैं?</h6>
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-outline-primary" id="cameraBtn">
                                    <i class="bi bi-camera"></i> कैमरा
                                </button>
                                <button type="button" class="btn btn-outline-primary" id="galleryBtn">
                                    <i class="bi bi-image"></i> गैलरी
                                </button>
                            </div>
                        </div>
                        
                        <!-- Camera Options -->
                        <div id="cameraOptions" class="text-center mb-4" style="display: none;">
                            <h6>कैमरा चुनें</h6>
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-outline-success" id="frontCameraBtn">
                                    <i class="bi bi-camera"></i> फ्रंट कैमरा
                                </button>
                                <button type="button" class="btn btn-outline-success" id="backCameraBtn">
                                    <i class="bi bi-camera-fill"></i> बैक कैमरा
                                </button>
                                <button type="button" class="btn btn-outline-secondary" id="backToOptionsBtn">
                                    <i class="bi bi-arrow-left"></i> वापस
                                </button>
                            </div>
                        </div>
                        
                        <!-- Live Camera Feed -->
                        <div id="cameraFeed" style="display: none;">
                            <div class="text-center mb-3">
                                <h6>फोटो लेने के लिए कैप्चर बटन दबाएं</h6>
                            </div>
                            <div class="camera-container text-center">
                                <video id="cameraVideo" autoplay playsinline style="max-width: 100%; border-radius: 8px;"></video>
                                <canvas id="cameraCanvas" style="display: none;"></canvas>
                            </div>
                            <div class="text-center mt-3">
                                <button type="button" class="btn btn-success" id="captureBtn">
                                    <i class="bi bi-camera"></i> कैप्चर करें
                                </button>
                                <button type="button" class="btn btn-secondary ms-2" id="stopCameraBtn">
                                    <i class="bi bi-x-circle"></i> बंद करें
                                </button>
                            </div>
                        </div>

                        <!-- File Input -->
                        <input type="file" id="documentFileInput" accept="image/*" style="display: none;">

                        <!-- Cropping Area -->
                        <div id="cropArea" style="display: none;">
                            <div class="text-center mb-3">
                                <h6>फोटो को क्रॉप करें</h6>
                                <small class="text-muted">फोटो को खींचें और ज़ूम करें</small>
                            </div>
                            
                            <!-- Mobile-friendly crop controls -->
                            <div class="crop-controls mb-3 d-block d-md-none">
                                <div class="btn-group w-100" role="group">
                                    <button type="button" class="btn btn-outline-secondary btn-sm" id="zoomInBtn">
                                        <i class="bi bi-zoom-in"></i> ज़ूम इन
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" id="zoomOutBtn">
                                        <i class="bi bi-zoom-out"></i> ज़ूम आउट
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" id="resetCropBtn">
                                        <i class="bi bi-arrow-clockwise"></i> रीसेट
                                    </button>
                                </div>
                            </div>
                            
                            <div class="crop-container" style="max-height: 400px; overflow: hidden;">
                                <img id="cropImage" style="max-width: 100%; display: block;">
                            </div>
                            
                            <!-- Crop instructions for mobile -->
                            <div class="crop-instructions d-block d-md-none mt-2">
                                <small class="text-muted">
                                    <i class="bi bi-info-circle"></i> 
                                    टिप: फोटो को खींचकर पोजीशन करें, पिंच करके ज़ूम करें
                                </small>
                            </div>
                        </div>

                        <!-- Loading Animation -->
                        <div id="loadingArea" style="display: none;" class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">फोटो को कंप्रेस कर रहे हैं...</p>
                            <div class="progress mt-2">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     id="compressionProgress" style="width: 0%"></div>
                            </div>
                        </div>

                        <!-- Preview Area -->
                        <div id="previewArea" style="display: none;" class="text-center">
                            <h6>अंतिम परिणाम</h6>
                            <img id="finalPreview" class="img-thumbnail" style="max-width: 200px;">
                            <p class="mt-2">
                                <small>फाइल साइज़: <span id="finalSize"></span></small>
                            </p>
                        </div>
                        
                        <!-- Upload Spinner -->
                        <div id="uploadSpinner" style="display: none;" class="text-center">
                            <div class="spinner-border text-success" role="status">
                                <span class="visually-hidden">Uploading...</span>
                            </div>
                            <p class="mt-2">फोटो अपलोड हो रही है...</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="cancelBtn">रद्द करें</button>
                        <button type="button" class="btn btn-outline-warning" id="skipCropBtn" style="display: none;">
                            <i class="bi bi-skip-forward"></i> क्रॉप नहीं करें
                        </button>
                        <button type="button" class="btn btn-primary" id="cropOkBtn" style="display: none;">
                            <i class="bi bi-crop"></i> क्रॉप करें
                        </button>
                        <button type="button" class="btn btn-success" id="finalOkBtn" style="display: none;">
                            <i class="bi bi-cloud-upload"></i> अपलोड करें
                        </button>
                    </div>
                </div>
            </div>
        </div>`;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    bindEvents() {
        // Camera button
        document.getElementById('cameraBtn').addEventListener('click', () => {
            this.showCameraOptions();
        });

        // Gallery button
        document.getElementById('galleryBtn').addEventListener('click', () => {
            this.openGallery();
        });
        
        // Front camera button
        document.getElementById('frontCameraBtn').addEventListener('click', () => {
            this.openCamera('user');
        });
        
        // Back camera button
        document.getElementById('backCameraBtn').addEventListener('click', () => {
            this.openCamera('environment');
        });
        
        // Back to options button
        document.getElementById('backToOptionsBtn').addEventListener('click', () => {
            this.showUploadOptions();
        });
        
        // Capture button
        document.getElementById('captureBtn').addEventListener('click', () => {
            this.capturePhoto();
        });
        
        // Stop camera button
        document.getElementById('stopCameraBtn').addEventListener('click', () => {
            this.stopCamera();
        });

        // File input change
        document.getElementById('documentFileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Crop OK button
        document.getElementById('cropOkBtn').addEventListener('click', () => {
            this.processCroppedImage();
        });
        
        // Skip crop button
        document.getElementById('skipCropBtn').addEventListener('click', () => {
            this.processOriginalImage();
        });
        
        // Mobile crop controls
        document.getElementById('zoomInBtn').addEventListener('click', () => {
            if (this.cropper) this.cropper.zoom(0.1);
        });
        
        document.getElementById('zoomOutBtn').addEventListener('click', () => {
            if (this.cropper) this.cropper.zoom(-0.1);
        });
        
        document.getElementById('resetCropBtn').addEventListener('click', () => {
            if (this.cropper) this.cropper.reset();
        });

        // Final OK button
        document.getElementById('finalOkBtn').addEventListener('click', () => {
            this.finalizeUpload();
        });

        // Modal close event
        document.getElementById('documentUploadModal').addEventListener('hidden.bs.modal', () => {
            this.stopCamera();
            this.resetModal();
        });
    }

    openUploader(fieldName) {
        this.currentFieldName = fieldName;
        
        // Check if camera is available
        this.checkCameraAvailability();
        
        const modal = new bootstrap.Modal(document.getElementById('documentUploadModal'));
        modal.show();
    }
    
    async checkCameraAvailability() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const hasCamera = devices.some(device => device.kind === 'videoinput');
            
            const cameraBtn = document.getElementById('cameraBtn');
            if (!hasCamera || !navigator.mediaDevices.getUserMedia) {
                cameraBtn.style.display = 'none';
            } else {
                cameraBtn.style.display = 'inline-block';
            }
        } catch (error) {
            // Hide camera button if there's an error checking
            document.getElementById('cameraBtn').style.display = 'none';
        }
    }

    showCameraOptions() {
        document.getElementById('uploadOptions').style.display = 'none';
        document.getElementById('cameraOptions').style.display = 'block';
    }
    
    showUploadOptions() {
        document.getElementById('cameraOptions').style.display = 'none';
        document.getElementById('cameraFeed').style.display = 'none';
        document.getElementById('uploadOptions').style.display = 'block';
        this.stopCamera();
    }
    
    async openCamera(facingMode = 'environment') {
        this.currentFacingMode = facingMode;
        
        try {
            // Stop any existing stream
            this.stopCamera();
            
            // Request camera access
            const constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            
            this.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            const video = document.getElementById('cameraVideo');
            video.srcObject = this.cameraStream;
            
            // Show camera feed
            document.getElementById('cameraOptions').style.display = 'none';
            document.getElementById('cameraFeed').style.display = 'block';
            
        } catch (error) {
            console.error('Camera access error:', error);
            let errorMessage = 'कैमरा एक्सेस में समस्या।';
            
            if (error.name === 'NotAllowedError') {
                errorMessage = 'कैमरा की अनुमति नहीं मिली। कृपया ब्राउज़र सेटिंग्स में कैमरा की अनुमति दें।';
            } else if (error.name === 'NotFoundError') {
                errorMessage = 'कोई कैमरा नहीं मिला।';
            }
            
            alert(errorMessage + ' कृपया गैलरी का उपयोग करें।');
            this.showUploadOptions();
        }
    }
    
    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        const canvas = document.getElementById('cameraCanvas');
        const context = canvas.getContext('2d');
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(video, 0, 0);
        
        // Convert canvas to blob
        canvas.toBlob((blob) => {
            if (blob) {
                // Create file from blob
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                this.currentFile = file;
                
                // Stop camera and show crop area
                this.stopCamera();
                this.showCropArea(file);
            }
        }, 'image/jpeg', 0.9);
    }
    
    stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        
        const video = document.getElementById('cameraVideo');
        if (video.srcObject) {
            video.srcObject = null;
        }
    }

    openGallery() {
        const fileInput = document.getElementById('documentFileInput');
        fileInput.removeAttribute('capture');
        fileInput.click();
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('कृपया केवल इमेज फाइल अपलोड करें');
            return;
        }

        this.currentFile = file;
        this.showCropArea(file);
    }

    showCropArea(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const cropImage = document.getElementById('cropImage');
            cropImage.src = e.target.result;

            // Hide upload options, show crop area
            document.getElementById('uploadOptions').style.display = 'none';
            document.getElementById('cropArea').style.display = 'block';
            document.getElementById('cropOkBtn').style.display = 'inline-block';
            document.getElementById('skipCropBtn').style.display = 'inline-block';

            // Initialize cropper
            if (this.cropper) {
                this.cropper.destroy();
            }

            this.cropper = new Cropper(cropImage, {
                aspectRatio: this.getAspectRatio(),
                viewMode: 1,
                autoCropArea: 0.9,
                responsive: true,
                restore: false,
                guides: false,
                center: false,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
                minCropBoxHeight: 100,
                minCropBoxWidth: 100,
                // Mobile-friendly settings
                wheelZoomRatio: 0.1,
                checkOrientation: false,
                modal: true,
                background: true,
                // Touch-friendly cropping
                movable: true,
                rotatable: false,
                scalable: true,
                zoomable: true,
                zoomOnTouch: true,
                zoomOnWheel: true,
                cropBoxResizable: window.innerWidth > 768, // Only allow resize on desktop
            });
        };
        reader.readAsDataURL(file);
    }

    getAspectRatio() {
        // Different aspect ratios for different document types
        if (this.currentFieldName === 'passport_photo') {
            return 1; // Square for passport photo
        }
        return 16/10; // Standard for Aadhar cards
    }

    async processCroppedImage() {
        if (!this.cropper) return;

        // Show loading
        document.getElementById('cropArea').style.display = 'none';
        document.getElementById('cropOkBtn').style.display = 'none';
        document.getElementById('skipCropBtn').style.display = 'none';
        document.getElementById('loadingArea').style.display = 'block';

        // Start progress animation
        this.animateProgress();

        try {
            // Get cropped canvas
            const canvas = this.cropper.getCroppedCanvas({
                width: this.getTargetWidth(),
                height: this.getTargetHeight(),
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            // Compress image
            const compressedBlob = await this.compressImage(canvas);
            
            // Show preview
            this.showPreview(compressedBlob);
        } catch (error) {
            console.error('Error processing image:', error);
            alert('फोटो प्रोसेसिंग में त्रुटि हुई');
            this.resetModal();
        }
    }
    
    async processOriginalImage() {
        if (!this.currentFile) return;

        // Show loading
        document.getElementById('cropArea').style.display = 'none';
        document.getElementById('cropOkBtn').style.display = 'none';
        document.getElementById('skipCropBtn').style.display = 'none';
        document.getElementById('loadingArea').style.display = 'block';

        // Start progress animation
        this.animateProgress();

        try {
            // Create canvas from original file
            const canvas = await this.createCanvasFromFile(this.currentFile);
            
            // Compress image
            const compressedBlob = await this.compressImage(canvas);
            
            // Show preview
            this.showPreview(compressedBlob);
        } catch (error) {
            console.error('Error processing image:', error);
            alert('फोटो प्रोसेसिंग में त्रुटि हुई');
            this.resetModal();
        }
    }
    
    async createCanvasFromFile(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Calculate dimensions maintaining aspect ratio
                const maxWidth = this.getTargetWidth();
                const maxHeight = this.getTargetHeight();
                
                let { width, height } = img;
                
                if (width > height) {
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = (width * maxHeight) / height;
                        height = maxHeight;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                ctx.drawImage(img, 0, 0, width, height);
                resolve(canvas);
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }

    getTargetWidth() {
        return this.currentFieldName === 'passport_photo' ? 400 : 800;
    }

    getTargetHeight() {
        return this.currentFieldName === 'passport_photo' ? 400 : 500;
    }

    async compressImage(canvas) {
        return new Promise((resolve) => {
            let quality = 0.8;
            
            const compress = () => {
                canvas.toBlob((blob) => {
                    if (blob.size <= this.maxFileSize || quality <= 0.1) {
                        resolve(blob);
                    } else {
                        quality -= 0.1;
                        setTimeout(compress, 100); // Small delay for progress animation
                    }
                }, 'image/jpeg', quality);
            };
            
            compress();
        });
    }

    animateProgress() {
        const progressBar = document.getElementById('compressionProgress');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            progressBar.style.width = progress + '%';
        }, 200);
    }

    showPreview(blob) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('finalPreview').src = e.target.result;
            document.getElementById('finalSize').textContent = this.formatFileSize(blob.size);
            
            // Hide loading, show preview
            document.getElementById('loadingArea').style.display = 'none';
            document.getElementById('previewArea').style.display = 'block';
            document.getElementById('finalOkBtn').style.display = 'inline-block';
            
            // Store the final blob
            this.finalBlob = blob;
        };
        reader.readAsDataURL(blob);
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    finalizeUpload() {
        if (!this.finalBlob || !this.currentFieldName) return;

        // Create file from blob
        const fileName = this.generateFileName();
        const file = new File([this.finalBlob], fileName, { type: 'image/jpeg' });

        // Create FormData and upload
        this.uploadFile(file);
    }
    
    showUploadSpinner() {
        // Hide preview area and show upload spinner
        document.getElementById('previewArea').style.display = 'none';
        document.getElementById('finalOkBtn').style.display = 'none';
        
        // Show upload loading
        const uploadSpinner = document.getElementById('uploadSpinner');
        if (uploadSpinner) {
            uploadSpinner.style.display = 'block';
        }
    }
    
    hideUploadSpinner() {
        const uploadSpinner = document.getElementById('uploadSpinner');
        if (uploadSpinner) {
            uploadSpinner.style.display = 'none';
        }
    }

    generateFileName() {
        const timestamp = Date.now();
        const docType = this.currentFieldName.replace('_', '-');
        return `${docType}-${timestamp}.jpg`;
    }

    async uploadFile(file) {
        // Show upload spinner
        this.showUploadSpinner();
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('field_name', this.currentFieldName);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        // Add user info for better file naming
        const nameField = document.querySelector('[name="full_name"]');
        const phoneField = document.querySelector('[name="phone"]');
        if (nameField && nameField.value) {
            formData.append('user_name', nameField.value);
        }
        if (phoneField && phoneField.value) {
            formData.append('user_id', phoneField.value);
        }

        try {
            const response = await fetch('/upload-document/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.updatePreview(result.file_url);
                this.closeModal();
            } else {
                alert('अपलोड में त्रुटि: ' + result.error);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('अपलोड में त्रुटि हुई');
        } finally {
            this.hideUploadSpinner();
        }
    }

    updatePreview(fileUrl) {
        const previewId = `${this.currentFieldName}_preview`;
        const preview = document.getElementById(previewId);
        const uploadCard = preview ? preview.closest('.document-upload-card') : null;
        
        if (preview) {
            preview.src = fileUrl;
            preview.style.display = 'block';
        }
        
        // Update upload card to show uploaded state
        if (uploadCard) {
            uploadCard.classList.add('uploaded');
            const uploadText = uploadCard.querySelector('.upload-text');
            const uploadSubtext = uploadCard.querySelector('.upload-subtext');
            const uploadIcon = uploadCard.querySelector('.upload-icon i');
            
            if (uploadText) {
                uploadText.innerHTML = '<span class="upload-success"><i class="bi bi-check-circle-fill"></i>अपलोड हो गया</span>';
            }
            if (uploadSubtext) {
                uploadSubtext.textContent = 'बदलने के लिए क्लिक करें';
            }
            if (uploadIcon) {
                uploadIcon.className = 'bi bi-check-circle-fill';
            }
        }

        // Update hidden input
        const hiddenInput = document.querySelector(`input[name="${this.currentFieldName}"]`);
        if (hiddenInput) {
            hiddenInput.value = fileUrl;
        }
        
        // Trigger validation after upload
        setTimeout(() => {
            validateDocuments();
        }, 100);
    }

    closeModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('documentUploadModal'));
        modal.hide();
    }

    resetModal() {
        // Stop camera first
        this.stopCamera();
        
        // Reset all areas
        document.getElementById('uploadOptions').style.display = 'block';
        document.getElementById('cameraOptions').style.display = 'none';
        document.getElementById('cameraFeed').style.display = 'none';
        document.getElementById('cropArea').style.display = 'none';
        document.getElementById('loadingArea').style.display = 'none';
        document.getElementById('previewArea').style.display = 'none';
        document.getElementById('uploadSpinner').style.display = 'none';
        
        // Reset buttons
        document.getElementById('cropOkBtn').style.display = 'none';
        document.getElementById('skipCropBtn').style.display = 'none';
        document.getElementById('finalOkBtn').style.display = 'none';
        
        // Reset progress
        document.getElementById('compressionProgress').style.width = '0%';
        
        // Destroy cropper
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }
        
        // Reset file input
        document.getElementById('documentFileInput').value = '';
        
        // Reset variables
        this.currentFile = null;
        this.currentFieldName = null;
        this.finalBlob = null;
    }
}

// Initialize uploader when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.documentUploader = new DocumentUploader();
    initializeExistingPreviews();
    initializeRealTimeValidation();
});

// Initialize previews for existing uploads
function initializeExistingPreviews() {
    const previewImages = document.querySelectorAll('.document-preview');
    previewImages.forEach(preview => {
        if (preview.src && preview.src !== window.location.href) {
            const uploadCard = preview.closest('.document-upload-card');
            if (uploadCard) {
                uploadCard.classList.add('uploaded');
                const uploadText = uploadCard.querySelector('.upload-text');
                const uploadSubtext = uploadCard.querySelector('.upload-subtext');
                const uploadIcon = uploadCard.querySelector('.upload-icon i');
                
                if (uploadText) {
                    uploadText.innerHTML = '<span class="upload-success"><i class="bi bi-check-circle-fill"></i>अपलोड हो गया</span>';
                }
                if (uploadSubtext) {
                    uploadSubtext.textContent = 'बदलने के लिए क्लिक करें';
                }
                if (uploadIcon) {
                    uploadIcon.className = 'bi bi-check-circle-fill';
                }
                preview.style.display = 'block';
            }
        }
    });
}

// Function to open uploader (called from HTML)
function openDocumentUploader(fieldName) {
    if (window.documentUploader) {
        window.documentUploader.openUploader(fieldName);
    }
}

// Real-time validation functions
function initializeRealTimeValidation() {
    // Aadhar type selection validation
    const aadharTypeRadios = document.querySelectorAll('input[name="aadhar_upload_type"]');
    aadharTypeRadios.forEach(radio => {
        radio.addEventListener('change', validateAadharUploads);
    });
    
    // Document upload validation
    const documentInputs = document.querySelectorAll('input[name^="aadhar_"], input[name="passport_photo"]');
    documentInputs.forEach(input => {
        input.addEventListener('change', validateDocuments);
    });
    
    // Initial validation
    validateAadharUploads();
    validateDocuments();
}

function validateAadharUploads() {
    const selectedType = document.querySelector('input[name="aadhar_upload_type"]:checked');
    
    if (selectedType) {
        const type = selectedType.value;
        
        // Hide all upload sections first
        document.querySelectorAll('.aadhar-uploads').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected upload section
        document.getElementById('aadhar_' + type + '_upload').classList.add('active');
        
        // Clear validation errors for non-selected type
        if (type === 'full') {
            clearValidationError('aadhar_front');
            clearValidationError('aadhar_back');
        } else {
            clearValidationError('aadhar_full');
        }
    }
}

function validateDocuments() {
    let isValid = true;
    
    // Clear all previous validation errors
    clearAllValidationErrors();
    
    // Check if user has uploaded aadhar in any valid way
    const hasFullAadhar = hasUploadedDocument('aadhar_full');
    const hasFrontBack = hasUploadedDocument('aadhar_front') && hasUploadedDocument('aadhar_back');
    
    if (!hasFullAadhar && !hasFrontBack) {
        // Show error based on selected type or general error
        const selectedType = document.querySelector('input[name="aadhar_upload_type"]:checked');
        
        if (selectedType) {
            const type = selectedType.value;
            if (type === 'full') {
                showValidationError('aadhar_full', 'पूरा आधार कार्ड अपलोड करना आवश्यक है');
            } else {
                if (!hasUploadedDocument('aadhar_front')) {
                    showValidationError('aadhar_front', 'आधार कार्ड (आगे) अपलोड करना आवश्यक है');
                }
                if (!hasUploadedDocument('aadhar_back')) {
                    showValidationError('aadhar_back', 'आधार कार्ड (पीछे) अपलोड करना आवश्यक है');
                }
            }
        } else {
            showValidationError('aadhar_type', 'आधार कार्ड अपलोड करना आवश्यक है (पूरा या आगे-पीछे)');
        }
        isValid = false;
    }
    
    // Validate passport photo
    if (!hasUploadedDocument('passport_photo')) {
        showValidationError('passport_photo', 'पासपोर्ट साइज़ फोटो अपलोड करना आवश्यक है');
        isValid = false;
    }
    
    return isValid;
}

function hasUploadedDocument(fieldName) {
    const input = document.querySelector(`input[name="${fieldName}"]`);
    return input && input.value && input.value.trim() !== '';
}

function showValidationError(fieldName, message) {
    const uploadCard = document.querySelector(`[onclick*="${fieldName}"]`);
    if (uploadCard) {
        uploadCard.classList.add('validation-error');
        
        // Remove existing error message
        const existingError = uploadCard.querySelector('.validation-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-message';
        errorDiv.textContent = message;
        uploadCard.appendChild(errorDiv);
    }
    
    // Special handling for aadhar type selection
    if (fieldName === 'aadhar_type') {
        const typeSelector = document.querySelector('.aadhar-type-selector');
        if (typeSelector) {
            typeSelector.classList.add('validation-error');
            
            const existingError = typeSelector.querySelector('.validation-message');
            if (existingError) {
                existingError.remove();
            }
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-message';
            errorDiv.textContent = message;
            typeSelector.appendChild(errorDiv);
        }
    }
}

function clearValidationError(fieldName) {
    const uploadCard = document.querySelector(`[onclick*="${fieldName}"]`);
    if (uploadCard) {
        uploadCard.classList.remove('validation-error');
        const errorMessage = uploadCard.querySelector('.validation-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
}

function clearAllValidationErrors() {
    // Clear upload card errors
    document.querySelectorAll('.document-upload-card').forEach(card => {
        card.classList.remove('validation-error');
        const errorMessage = card.querySelector('.validation-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    });
    
    // Clear type selector errors
    const typeSelector = document.querySelector('.aadhar-type-selector');
    if (typeSelector) {
        typeSelector.classList.remove('validation-error');
        const errorMessage = typeSelector.querySelector('.validation-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
}

// Override form submission to validate documents
function validateFormBeforeSubmit() {
    return validateDocuments();
}