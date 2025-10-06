// Optimized final approval workflow - generates documents simultaneously and sends email with attachments
(function($) {
    'use strict';

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

    function getVehicleNumber() {
        const field = $('input[name="vehicle_number"], #id_vehicle_number');
        if (field.length) return field.val();
        const text = $('.field-vehicle_number .readonly');
        if (text.length) return text.text().trim();
        return null;
    }

    function processApproval(registrationId, formData) {
        showProgress('🚀 Starting approval process...');
        
        const vehicleNumber = getVehicleNumber();
        const transportMode = $('select[name="transport_mode"], #id_transport_mode').val() || 
                             $('.field-transport_mode .readonly').text().trim();
        
        // Step 1: Generate ID Card
        updateProgress('📄 Generating ID card...');
        $.get(`/id/card/${registrationId}/`)
            .done(function() {
                updateProgress('✅ ID card generated successfully');
                
                // Step 2: Check vehicle pass requirement
                if (vehicleNumber && 
                    vehicleNumber.trim() !== '' && 
                    vehicleNumber.trim() !== '-' && 
                    transportMode === 'car') {
                    
                    updateProgress('🚗 Generating vehicle pass...');
                    const encodedVehicle = encodeURIComponent(vehicleNumber);
                    
                    $.get(`/vehicle-pass/generate/${registrationId}/${encodedVehicle}/`)
                        .done(function() {
                            updateProgress('✅ Vehicle pass generated successfully');
                            processApprovalStep(registrationId, formData);
                        })
                        .fail(function() {
                            updateProgress('⚠️ Vehicle pass generation failed, continuing...');
                            processApprovalStep(registrationId, formData);
                        });
                } else {
                    updateProgress('⚠️ Vehicle pass skipped (no valid vehicle info)');
                    processApprovalStep(registrationId, formData);
                }
            })
            .fail(function() {
                updateProgress('❌ ID card generation failed');
                setTimeout(hideProgress, 3000);
            });
    }
    
    function processApprovalStep(registrationId, formData) {
        // Step 3: Process approval
        updateProgress('📝 Processing approval status...');
        
        let approvalData = formData + '&_skip_auto_email=1';
        if (!approvalData.includes('approval_status=approved')) {
            approvalData = approvalData.replace(/approval_status=[^&]*/, 'approval_status=approved');
            if (!approvalData.includes('approval_status=')) {
                approvalData += '&approval_status=approved';
            }
        }
        
        $.post(window.location.href, approvalData)
            .done(function() {
                updateProgress('✅ Approval status updated successfully');
                
                // Step 4: Send email
                updateProgress('📧 Sending combined email with attachments...');
                
                $.get(`/resend-email/${registrationId}/`)
                    .done(function() {
                        updateProgress('✅ Email sent successfully! Redirecting...');
                        
                        setTimeout(function() {
                            hideProgress();
                            alert('🎉 Process completed successfully!\n\n✅ ID card generated\n✅ Vehicle pass handled\n✅ Approval processed\n✅ Email sent with attachments');
                            
                            const url = window.location.href;
                            if (url.includes('_continue=1')) {
                                window.location.reload();
                            } else if (url.includes('_addanother=1')) {
                                window.location.href = window.location.pathname.replace(/\/\d+\/change\//, '/add/');
                            } else {
                                window.location.href = window.location.pathname.replace(/\/\d+\/change\//, '/');
                            }
                        }, 1500);
                    })
                    .fail(function() {
                        updateProgress('❌ Email sending failed');
                        setTimeout(hideProgress, 3000);
                    });
            })
            .fail(function() {
                updateProgress('❌ Approval processing failed');
                setTimeout(hideProgress, 3000);
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