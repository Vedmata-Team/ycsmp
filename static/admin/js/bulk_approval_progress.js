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
    
    // Make AJAX request with streaming
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => {
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
        updateProgress('error', 'Connection error occurred', 0);
        console.error('Streaming error:', error);
    });
}

function showProgressModal() {
    const modal = document.createElement('div');
    modal.id = 'bulk-progress-modal';
    modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 30px; border-radius: 8px; min-width: 400px; text-align: center;">
                <h3>🔄 Processing Bulk Approval...</h3>
                <div id="progress-status" style="margin: 20px 0; font-size: 16px; color: #666;">
                    Initializing...
                </div>
                <div style="width: 100%; background: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 20px 0;">
                    <div id="progress-bar" style="width: 0%; height: 20px; background: #28a745; transition: width 0.3s;"></div>
                </div>
                <div id="progress-details" style="font-size: 14px; color: #888; margin-top: 10px;">
                    Please wait...
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function updateProgress(step, message, progress) {
    const statusEl = document.getElementById('progress-status');
    const barEl = document.getElementById('progress-bar');
    const detailsEl = document.getElementById('progress-details');
    
    if (statusEl) statusEl.textContent = message;
    if (barEl) barEl.style.width = progress + '%';
    if (detailsEl) detailsEl.textContent = `${step} - ${progress}% complete`;
}