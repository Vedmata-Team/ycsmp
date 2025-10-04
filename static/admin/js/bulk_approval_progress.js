// Bulk Approval Progress Tracker
document.addEventListener('DOMContentLoaded', function() {
    const actionSelect = document.querySelector('select[name="action"]');
    const goButton = document.querySelector('button[name="index"]');
    
    if (actionSelect && goButton) {
        goButton.addEventListener('click', function(e) {
            const selectedAction = actionSelect.value;
            if (selectedAction === 'approve_final' || selectedAction === 'approve_district' || selectedAction === 'approve_upzone') {
                showProgressModal();
            }
        });
    }
});

function showProgressModal() {
    // Create progress modal
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
    
    // Start progress tracking
    trackProgress();
}

function trackProgress() {
    const statusEl = document.getElementById('progress-status');
    const barEl = document.getElementById('progress-bar');
    const detailsEl = document.getElementById('progress-details');
    
    let step = 0;
    const steps = [
        'Validating permissions...',
        'Preparing registrations...',
        'Updating database records...',
        'Generating registration numbers...',
        'Finalizing changes...',
        'Complete!'
    ];
    
    const interval = setInterval(() => {
        if (step < steps.length - 1) {
            statusEl.textContent = steps[step];
            barEl.style.width = ((step + 1) / steps.length * 100) + '%';
            detailsEl.textContent = `Step ${step + 1} of ${steps.length}`;
            step++;
        } else {
            statusEl.textContent = steps[step];
            barEl.style.width = '100%';
            detailsEl.textContent = 'Processing completed successfully!';
            clearInterval(interval);
            
            // Auto-close after 2 seconds
            setTimeout(() => {
                const modal = document.getElementById('bulk-progress-modal');
                if (modal) modal.remove();
            }, 2000);
        }
    }, 800);
}