// Bulk Email Sender - Processes emails one by one to avoid timeouts
(function($) {
    'use strict';

    let emailQueue = [];
    let currentIndex = 0;
    let totalEmails = 0;
    let successCount = 0;
    let failCount = 0;
    let isProcessing = false;

    function showBulkProgress() {
        const modal = $(`
            <div id="bulk-email-modal" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.8); z-index: 10000; display: flex; 
                align-items: center; justify-content: center;
            ">
                <div style="
                    background: #ffffff; padding: 30px; border-radius: 12px; 
                    text-align: center; min-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                ">
                    <h3 style="margin: 0 0 20px 0; color: #333;">⚡ Bulk Email Sending</h3>
                    <div style="
                        background: #f8f9fa; border-radius: 8px; padding: 10px; margin-bottom: 20px;
                    ">
                        <div id="bulk-progress-bar" style="
                            background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                            height: 12px; border-radius: 6px; width: 0%; transition: width 0.3s ease;
                        "></div>
                    </div>
                    <p id="bulk-progress-text" style="
                        margin: 0 0 15px 0; font-size: 16px; font-weight: bold; color: #333;
                    ">Preparing...</p>
                    <div id="bulk-stats" style="
                        display: flex; justify-content: space-around; margin-bottom: 20px;
                        font-size: 14px; color: #666;
                    ">
                        <span>✅ Success: <strong id="success-count">0</strong></span>
                        <span>❌ Failed: <strong id="fail-count">0</strong></span>
                        <span>📧 Total: <strong id="total-count">0</strong></span>
                    </div>
                    <button id="cancel-bulk" style="
                        background: #dc3545; color: white; border: none; padding: 8px 16px;
                        border-radius: 4px; cursor: pointer; display: none;
                    ">Cancel</button>
                </div>
            </div>
        `);
        $('body').append(modal);
        
        $('#cancel-bulk').click(function() {
            isProcessing = false;
            hideBulkProgress();
        });
    }

    function updateBulkProgress(text, percentage) {
        $('#bulk-progress-text').text(text);
        $('#bulk-progress-bar').css('width', percentage + '%');
        $('#success-count').text(successCount);
        $('#fail-count').text(failCount);
        $('#total-count').text(totalEmails);
    }

    function hideBulkProgress() {
        $('#bulk-email-modal').remove();
    }

    function startRealTimeStream(selectedIds) {
        const eventSource = new EventSource(`/stream-bulk-email/?ids=${selectedIds.join(',')}`);
        
        // Add console output area
        $('#bulk-email-modal .modal-content').append(`
            <div id="console-output" style="
                background: #000; color: #00ff00; padding: 10px; margin: 10px 0;
                border-radius: 4px; font-family: monospace; font-size: 12px;
                height: 200px; overflow-y: auto; white-space: pre-wrap;
            ">Real-time console output will appear here...</div>
        `);
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'start':
                    totalEmails = data.total;
                    updateBulkProgress(data.message, 0);
                    break;
                    
                case 'progress':
                    const progress = (data.current / data.total) * 100;
                    updateBulkProgress(data.message, progress);
                    break;
                    
                case 'email_result':
                    const resultProgress = (data.current / data.total) * 100;
                    successCount = data.success_count;
                    failCount = data.fail_count;
                    
                    updateBulkProgress(data.message, resultProgress);
                    
                    // Show real-time console output
                    if (data.console_output) {
                        const consoleDiv = $('#console-output');
                        consoleDiv.append(data.console_output + '\n');
                        consoleDiv.scrollTop(consoleDiv[0].scrollHeight);
                    }
                    break;
                    
                case 'complete':
                    updateBulkProgress(data.message, 100);
                    $('#cancel-bulk').text('Close').show();
                    eventSource.close();
                    
                    setTimeout(() => {
                        hideBulkProgress();
                        window.location.reload();
                    }, 3000);
                    break;
            }
        };
        
        eventSource.onerror = function() {
            updateBulkProgress('❌ Connection error', 0);
            $('#cancel-bulk').text('Close').show();
            eventSource.close();
        };
        
        // Handle cancel
        $('#cancel-bulk').off('click').on('click', function() {
            eventSource.close();
            hideBulkProgress();
        });
    }

    function startBulkEmailSending(selectedIds) {
        if (selectedIds.length === 0) {
            alert('Please select registrations to send emails to.');
            return;
        }

        if (isProcessing) {
            alert('Bulk email sending is already in progress.');
            return;
        }

        // Initialize
        emailQueue = selectedIds;
        currentIndex = 0;
        totalEmails = selectedIds.length;
        successCount = 0;
        failCount = 0;
        isProcessing = true;

        showBulkProgress();
        updateBulkProgress('Starting bulk email sending...', 0);
        
        // Start real-time streaming
        setTimeout(() => startRealTimeStream(selectedIds), 1000);
    }

    // Add bulk email action
    $(document).ready(function() {
        // Add custom bulk email button
        const bulkEmailButton = $(`
            <button type="button" id="bulk-email-btn" style="
                background: #28a745; color: white; border: none; padding: 8px 16px;
                border-radius: 4px; cursor: pointer; margin-left: 10px;
            ">⚡ Send Bulk Emails</button>
        `);
        
        $('.actions').append(bulkEmailButton);
        
        $('#bulk-email-btn').click(function() {
            const selectedIds = [];
            $('input[name="_selected_action"]:checked').each(function() {
                selectedIds.push($(this).val());
            });
            
            if (selectedIds.length === 0) {
                alert('Please select registrations first.');
                return;
            }
            
            if (confirm(`Send emails to ${selectedIds.length} selected registrations?`)) {
                startBulkEmailSending(selectedIds);
            }
        });
    });

})(django.jQuery);