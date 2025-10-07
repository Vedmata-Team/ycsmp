from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import EventRegistration
from .email_utils import send_registration_approval_email
import json
import time
import sys
from io import StringIO

@staff_member_required
def stream_bulk_email(request):
    """Stream real-time email sending progress"""
    
    # Get selected registration IDs
    selected_ids = request.GET.get('ids', '').split(',')
    selected_ids = [id for id in selected_ids if id.isdigit()]
    
    if not selected_ids:
        return StreamingHttpResponse("No registrations selected", content_type='text/plain')
    
    def generate_stream():
        registrations = EventRegistration.objects.filter(
            id__in=selected_ids,
            approval_status='approved'
        )
        
        total = registrations.count()
        success_count = 0
        fail_count = 0
        
        # Send initial status
        yield f"data: {json.dumps({'type': 'start', 'total': total, 'message': f'Starting bulk email for {total} registrations...'})}\n\n"
        
        for i, registration in enumerate(registrations):
            current = i + 1
            
            # Capture console output
            old_stdout = sys.stdout
            captured_output = StringIO()
            sys.stdout = captured_output
            
            try:
                # Send status update
                yield f"data: {json.dumps({'type': 'progress', 'current': current, 'total': total, 'message': f'Sending email to {registration.full_name} ({registration.email})...'})}\n\n"
                
                # Send email and capture output
                success = send_registration_approval_email(registration)
                
                # Get captured output
                console_output = captured_output.getvalue()
                sys.stdout = old_stdout
                
                if success:
                    success_count += 1
                    status = 'success'
                    message = f'✅ Email sent to {registration.email}'
                else:
                    fail_count += 1
                    status = 'failed'
                    message = f'❌ Email failed for {registration.email}'
                
                # Send detailed status with console output
                yield f"data: {json.dumps({'type': 'email_result', 'current': current, 'total': total, 'status': status, 'message': message, 'console_output': console_output, 'success_count': success_count, 'fail_count': fail_count})}\n\n"
                
                # Small delay between emails
                time.sleep(0.5)
                
            except Exception as e:
                sys.stdout = old_stdout
                fail_count += 1
                error_msg = f'❌ Error for {registration.email}: {str(e)}'
                yield f"data: {json.dumps({'type': 'email_result', 'current': current, 'total': total, 'status': 'error', 'message': error_msg, 'console_output': captured_output.getvalue(), 'success_count': success_count, 'fail_count': fail_count})}\n\n"
        
        # Send completion status
        yield f"data: {json.dumps({'type': 'complete', 'success_count': success_count, 'fail_count': fail_count, 'message': f'Completed! {success_count} sent, {fail_count} failed'})}\n\n"
    
    response = StreamingHttpResponse(generate_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response