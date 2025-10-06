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
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 99999; display: flex; align-items: center; justify-content: center;">
            <div style="background: #ffffff; padding: 50px; border-radius: 15px; min-width: 550px; max-width: 650px; text-align: center; box-shadow: 0 15px 40px rgba(0,0,0,0.4); border: 2px solid #007cba;">
                <div style="margin-bottom: 25px;">
                    <div class="spinner" style="width: 50px; height: 50px; border: 5px solid #e3f2fd; border-top: 5px solid #007cba; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <h3 style="color: #007cba; margin: 0; font-size: 24px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🔄 बल्क अप्रूवल प्रोसेसिंग</h3>
                </div>
                <div id="progress-status" style="margin: 30px 0; font-size: 20px; color: #000000 !important; font-weight: bold !important; background: #ffeb3b !important; padding: 20px; border-radius: 8px; border: 3px solid #000000 !important; text-align: center;">
                    प्रारंभ हो रहा है...
                </div>
                <div style="width: 100%; background: #e9ecef; border-radius: 20px; overflow: hidden; margin: 30px 0; height: 30px; border: 1px solid #dee2e6;">
                    <div id="progress-bar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.5s ease; border-radius: 20px;"></div>
                </div>
                <div id="progress-details" style="font-size: 18px; color: #000000 !important; margin-top: 20px; font-weight: bold !important; background: #e3f2fd !important; padding: 15px; border-radius: 6px; border: 2px solid #000000 !important; text-align: center;">
                    कृपया प्रतीक्षा करें...
                </div>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #bulk-progress-modal * {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
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
    
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.style.color = '#000000';
        statusEl.style.fontWeight = 'bold';
        statusEl.style.fontSize = '20px';
        statusEl.style.background = '#ffeb3b';
        statusEl.style.border = '3px solid #000000';
    }
    
    if (barEl) {
        barEl.style.width = progress + '%';
        if (step === 'completed') {
            barEl.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
            statusEl.style.background = '#d4edda';
            statusEl.style.borderLeftColor = '#28a745';
        } else if (step === 'error') {
            barEl.style.background = '#dc3545';
            statusEl.style.background = '#f8d7da';
            statusEl.style.borderLeftColor = '#dc3545';
        }
    }
    
    if (detailsEl) {
        if (step === 'completed') {
            detailsEl.textContent = '✅ सभी पंजीकरण अप्रूव हो गए';
            detailsEl.style.color = '#000000';
            detailsEl.style.fontWeight = 'bold';
            detailsEl.style.background = '#4caf50';
            detailsEl.style.border = '2px solid #000000';
        } else if (step === 'error') {
            detailsEl.textContent = '❌ कृपया पुनः प्रयास करें';
            detailsEl.style.color = '#ffffff';
            detailsEl.style.fontWeight = 'bold';
            detailsEl.style.background = '#f44336';
            detailsEl.style.border = '2px solid #000000';
        } else {
            detailsEl.textContent = `${progress}% पूरा हो गया`;
            detailsEl.style.color = '#000000';
            detailsEl.style.fontWeight = 'bold';
            detailsEl.style.fontSize = '18px';
            detailsEl.style.background = '#e3f2fd';
            detailsEl.style.border = '2px solid #000000';
        }
    }
}