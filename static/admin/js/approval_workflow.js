// Clean Approval Workflow - Handles approval with email sending
(function() {
    'use strict';
    
    // Check if jQuery is available
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        console.warn('Django jQuery not available, approval workflow disabled');
        return;
    }
    
    const $ = django.jQuery;
    
    function showProgress(message) {
        const modal = $(`
            <div id="approval-modal" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.8); z-index: 10000; display: flex; 
                align-items: center; justify-content: center;
            ">
                <div style="
                    background: #ffffff; padding: 40px; border-radius: 12px; 
                    text-align: center; min-width: 350px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                ">
                    <div style="
                        border: 4px solid #e3e3e3; border-top: 4px solid #007cba; 
                        border-radius: 50%; width: 50px; height: 50px; 
                        animation: spin 1s linear infinite; margin: 0 auto 20px;
                    "></div>
                    <p id="progress-text" style="
                        margin: 0; font-size: 16px; font-weight: bold; 
                        color: #333333 !important; line-height: 1.4;
                    ">${message}</p>
                </div>
            </div>
            <style>
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        `);
        $('body').append(modal);
    }

    function updateProgress(message) {
        $('#progress-text').text(message).css({
            'color': '#333333',
            'font-weight': 'bold',
            'font-size': '16px'
        });
    }

    function hideProgress() {
        $('#approval-modal').remove();
    }

    function processApproval(registrationId, formData) {
        showProgress('🚀 Starting approval process...');
        
        // Process approval step
        updateProgress('📝 Processing approval status...');
        
        // Ensure approval status is set to approved
        let approvalData = formData;
        if (!approvalData.includes('approval_status=approved')) {
            approvalData = approvalData.replace(/approval_status=[^&]*/, 'approval_status=approved');
            if (!approvalData.includes('approval_status=')) {
                approvalData += '&approval_status=approved';
            }
        }
        
        // Submit the form data
        $.post(window.location.href, approvalData)
            .done(function() {
                updateProgress('✅ Approval status updated successfully');
                
                // Send email
                updateProgress('📧 Sending approval email...');
                
                $.get(`/resend-email/${registrationId}/`)
                    .done(function() {
                        updateProgress('✅ Email sent successfully! Redirecting...');
                        
                        setTimeout(function() {
                            hideProgress();
                            alert('🎉 Process completed successfully!\\n\\n✅ Registration approved\\n📧 Email sent');
                            
                            // Redirect based on button clicked
                            const url = window.location.href;
                            if (url.includes('_continue=1')) {
                                window.location.reload();
                            } else if (url.includes('_addanother=1')) {
                                window.location.href = window.location.pathname.replace(/\/\d+\/change\//, '/add/');
                            } else {
                                // Go back to changelist with preserved filters
                                const changelist = window.location.pathname.replace(/\/\d+\/change\//, '/');
                                const params = new URLSearchParams(window.location.search);
                                params.delete('_continue');
                                params.delete('_addanother');
                                const queryString = params.toString();
                                window.location.href = changelist + (queryString ? '?' + queryString : '');
                            }
                        }, 1000);
                    })
                    .fail(function() {
                        updateProgress('⚠️ Email sending failed, but approval saved');
                        setTimeout(function() {
                            hideProgress();
                            alert('Registration approved but email failed to send.\\nYou can resend the email manually.');
                            window.location.reload();
                        }, 2000);
                    });
            })
            .fail(function() {
                updateProgress('❌ Approval processing failed');
                setTimeout(function() {
                    hideProgress();
                    alert('Failed to process approval. Please try again.');
                }, 2000);
            });
    }

    function isApprovalStatus() {
        const field = $('select[name="approval_status"], #id_approval_status');
        return field.length && field.val() === 'approved';
    }

    function getRegistrationId() {
        const match = window.location.pathname.match(/\/(\d+)\/change\//);
        return match ? match[1] : null;
    }

    $(document).ready(function() {
        console.log('Approval workflow loaded');
        
        // Handle final approval button
        $('input[name="_approve_final"]').click(function(e) {
            e.preventDefault();
            const form = $(this).closest('form');
            const formData = form.serialize() + '&_approve_final=1';
            const registrationId = getRegistrationId();
            
            if (registrationId && confirm('Process final approval and send email?')) {
                processApproval(registrationId, formData);
            }
        });
        
        // Handle save buttons when status is approved
        $('input[name="_save"], input[name="_addanother"], input[name="_continue"]').click(function(e) {
            if (isApprovalStatus()) {
                e.preventDefault();
                const form = $(this).closest('form');
                const buttonName = $(this).attr('name');
                const formData = form.serialize() + '&' + buttonName + '=1';
                const registrationId = getRegistrationId();
                
                if (registrationId && confirm('Process approval and send email?')) {
                    processApproval(registrationId, formData);
                }
            }
        });
    });

})();