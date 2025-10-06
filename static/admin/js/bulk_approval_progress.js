// Real-time Bulk Approval Progress Tracker
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#changelist-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const actionSelect = document.querySelector('select[name="action"]');
            const selectedAction = actionSelect ? actionSelect.value : '';
            
            if (selectedAction === 'approve_final') {
                e.preventDefault();
                startRealTimeApproval();
            }
        });
    }
});

function startRealTimeApproval() {
    const form = document.querySelector('#changelist-form');
    const formData = new FormData(form);
    
    // Ensure action is set
    formData.set('action', 'approve_final');
    
    // Show progress modal
    showProgressModal();
    
    // Make streaming request
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        function readStream() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    setTimeout(() => {
                        const modal = document.getElementById('bulk-progress-modal');
                        if (modal) modal.remove();
                        location.reload();
                    }, 2000);
                    return;
                }
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            updateProgress(data.step, data.message, data.progress);
                        } catch (e) {
                            console.log('Parse error:', e);
                        }
                    }
                });
                
                return readStream();
            });
        }
        
        return readStream();
    }).catch(error => {
        updateProgress('error', 'कनेक्शन त्रुटि हुई', 0);
        console.error('Streaming error:', error);
        
        setTimeout(() => {
            const modal = document.getElementById('bulk-progress-modal');
            if (modal) modal.remove();
        }, 3000);
    });
}

function showProgressModal() {
    const modal = document.createElement('div');
    modal.id = 'bulk-progress-modal';
    modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 40px; border-radius: 12px; min-width: 500px; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <div style="margin-bottom: 20px;">
                    <div class="spinner" style="width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #007cba; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px;"></div>
                    <h3 style="color: #007cba; margin: 0; font-size: 20px;">🔄 बल्क अप्रूवल प्रोसेसिंग</h3>
                </div>
                <div id="progress-status" style="margin: 25px 0; font-size: 16px; color: #333; font-weight: 500;">
                    प्रारंभ हो रहा है...
                </div>
                <div style="width: 100%; background: #e9ecef; border-radius: 15px; overflow: hidden; margin: 25px 0; height: 25px;">
                    <div id="progress-bar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.5s ease; border-radius: 15px;"></div>
                </div>
                <div id="progress-details" style="font-size: 14px; color: #6c757d; margin-top: 15px;">
                    कृपया प्रतीक्षा करें...
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
    document.body.appendChild(modal);
    
    // Start progress animation
    setTimeout(() => {
        updateProgress('processing', 'पंजीकरण प्रोसेस हो रहे हैं...', 10);
    }, 500);
}

function updateProgress(step, message, progress) {
    const statusEl = document.getElementById('progress-status');
    const barEl = document.getElementById('progress-bar');
    const detailsEl = document.getElementById('progress-details');
    
    if (statusEl) statusEl.textContent = message;
    if (barEl) {
        barEl.style.width = progress + '%';
        if (step === 'completed') {
            barEl.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
        } else if (step === 'error') {
            barEl.style.background = '#dc3545';
        }
    }
    if (detailsEl) {
        if (step === 'completed') {
            detailsEl.textContent = '✅ सभी पंजीकरण अप्रूव हो गए';
            detailsEl.style.color = '#28a745';
        } else if (step === 'error') {
            detailsEl.textContent = '❌ कृपया पुनः प्रयास करें';
            detailsEl.style.color = '#dc3545';
        } else {
            detailsEl.textContent = `${progress}% पूरा हो गया`;
        }
    }
}