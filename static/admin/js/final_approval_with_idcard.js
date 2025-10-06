// Optimized final approval workflow - generates documents simultaneously and sends email with attachments
(function($) {
    'use strict';

    function showProgress(message) {
        const modal = $(`
            <div id="approval-modal" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.9); z-index: 10000; display: flex; 
                align-items: center; justify-content: center;
            ">
                <div style="
                    background: white; padding: 30px; border-radius: 10px; 
                    text-align: center; min-width: 300px;
                ">
                    <div style="
                        border: 3px solid #f3f3f3; border-top: 3px solid #3498db; 
                        border-radius: 50%; width: 40px; height: 40px; 
                        animation: spin 1s linear infinite; margin: 0 auto 15px;
                    "></div>
                    <p id="progress-text" style="margin: 0; font-size: 14px;">${message}</p>
                </div>
            </div>
            <style>
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        `);
        $('body').append(modal);
    }

    function updateProgress(message) {
        $('#progress-text').text(message);
    }

    function hideProgress() {
        $('#approval-modal').remove();
    }

    function getVehicleNumber() {
        const field = $('input[name="vehicle_number"], #id_vehicle_number');
        if (field.length) return field.val();
        const text = $('.field-vehicle_number .readonly');
        if (text.length) return text.text().trim();
        return null;
    }

    function processApproval(registrationId, formData) {
        showProgress('Generating documents and processing approval...');
        
        const vehicleNumber = getVehicleNumber();
        const requests = [];
        
        // Always generate ID card
        requests.push($.get(`/id/card/${registrationId}/`));
        
        // Generate vehicle pass if needed
        if (vehicleNumber && vehicleNumber.trim()) {
            const encodedVehicle = encodeURIComponent(vehicleNumber);
            requests.push($.get(`/vehicle-pass/generate/${registrationId}/${encodedVehicle}/`));
        }
        
        // Generate documents simultaneously
        $.when.apply($, requests).always(function() {
            updateProgress('Documents generated, processing approval...');
            
            // Process approval with skip auto email
            let approvalData = formData + '&_skip_auto_email=1';
            if (!approvalData.includes('approval_status=approved')) {
                approvalData = approvalData.replace(/approval_status=[^&]*/, 'approval_status=approved');
                if (!approvalData.includes('approval_status=')) {
                    approvalData += '&approval_status=approved';
                }
            }
            
            $.post(window.location.href, approvalData).always(function() {
                updateProgress('Sending email with attachments...');
                
                // Send email with attachments
                $.get(`/resend-email/${registrationId}/`).always(function() {
                    hideProgress();
                    
                    // Show success and redirect
                    alert('✅ Approval completed successfully!\n\n• ID card generated\n• Vehicle pass generated\n• Email sent with attachments');
                    
                    const url = window.location.href;
                    if (url.includes('_continue=1')) {
                        window.location.reload();
                    } else if (url.includes('_addanother=1')) {
                        window.location.href = window.location.pathname.replace(/\/\d+\/change\//, '/add/');
                    } else {
                        window.location.href = window.location.pathname.replace(/\/\d+\/change\//, '/');
                    }
                });
            });
        });
    }

    function isApprovalStatus() {
        const field = $('select[name="approval_status"], #id_approval_status');
        return field.length && field.val() === 'approved';
    }

    $(document).ready(function() {
        // Handle final approval button
        $('input[name="_approve_final"]').click(function(e) {
            e.preventDefault();
            const form = $(this).closest('form');
            const formData = form.serialize() + '&_approve_final=1';
            const registrationId = window.location.pathname.match(/\/(\d+)\/change\//)[1];
            
            if (confirm('Process final approval with ID card, vehicle pass and email?')) {
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
                const registrationId = window.location.pathname.match(/\/(\d+)\/change\//)[1];
                
                if (confirm('Process approval with ID card, vehicle pass and email?')) {
                    processApproval(registrationId, formData);
                }
            }
        });
    });

})(django.jQuery);