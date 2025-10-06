#!/usr/bin/env python3
"""
Optimized Email System for User Approval
Fixes slow email sending and attachment generation issues
"""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import io
import tempfile
import os
import threading
import time

class OptimizedEmailSender:
    def __init__(self):
        self.attachment_cache = {}
    
    def generate_attachments_async(self, registration):
        """Generate attachments in background thread"""
        def generate():
            attachments = {}
            
            # Only generate if user has vehicle
            if registration.vehicle_number and registration.transport_mode == 'car':
                try:
                    # Generate ID card
                    id_card_data = self.generate_id_card_fast(registration)
                    if id_card_data:
                        attachments['id_card'] = {
                            'filename': f"id_card_{registration.registration_number or registration.id}.png",
                            'data': id_card_data,
                            'content_type': 'image/png'
                        }
                    
                    # Generate vehicle pass
                    vehicle_pass_data = self.generate_vehicle_pass_fast(registration)
                    if vehicle_pass_data:
                        attachments['vehicle_pass'] = {
                            'filename': f"vehicle_pass_{registration.registration_number or registration.id}.png",
                            'data': vehicle_pass_data,
                            'content_type': 'image/png'
                        }
                    
                    self.attachment_cache[registration.id] = attachments
                    print(f"Attachments generated for registration {registration.id}")
                    
                except Exception as e:
                    print(f"Error generating attachments: {e}")
                    self.attachment_cache[registration.id] = {}
            else:
                # Only ID card for non-vehicle users
                try:
                    id_card_data = self.generate_id_card_fast(registration)
                    if id_card_data:
                        attachments = {
                            'id_card': {
                                'filename': f"id_card_{registration.registration_number or registration.id}.png",
                                'data': id_card_data,
                                'content_type': 'image/png'
                            }
                        }
                        self.attachment_cache[registration.id] = attachments
                    else:
                        self.attachment_cache[registration.id] = {}
                except Exception as e:
                    print(f"Error generating ID card: {e}")
                    self.attachment_cache[registration.id] = {}
        
        # Start background thread
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
        return thread
    
    def generate_id_card_fast(self, registration):
        """Fast ID card generation with minimal overhead"""
        try:
            from ID.fallback_views import generate_id_card_with_fallback
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get(f'/id/card/{registration.id}/')
            response = generate_id_card_with_fallback(request, registration.id)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Fast ID card generation failed: {e}")
            return None
    
    def generate_vehicle_pass_fast(self, registration):
        """Fast vehicle pass generation with minimal overhead"""
        try:
            from vehicle_pass.views import generate_vehicle_pass
            from django.test import RequestFactory
            from urllib.parse import quote
            
            factory = RequestFactory()
            encoded_vehicle = quote(registration.vehicle_number, safe='')
            request = factory.get(f'/vehicle-pass/generate/{registration.id}/{encoded_vehicle}/')
            response = generate_vehicle_pass(request, registration.id, registration.vehicle_number)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Fast vehicle pass generation failed: {e}")
            return None
    
    def send_optimized_approval_email(self, registration, sent_by_user=None):
        """Send optimized approval email with smart attachment handling"""
        print(f"\n=== OPTIMIZED EMAIL SENDING ===")
        print(f"Registration: {registration.full_name}")
        print(f"Email: {registration.email}")
        print(f"Has vehicle: {bool(registration.vehicle_number and registration.transport_mode == 'car')}")
        
        # Determine registration type
        if registration.registration_type == 'volunteer':
            reg_type = 'समयदानी कार्यकर्ता'
        elif registration.registration_type == 'organization_representative':
            reg_type = 'संगठन प्रतिनिधि'
        else:
            reg_type = 'प्रतिभागी'
        
        subject = f'{reg_type} पंजीकरण अप्रूव - {registration.event.title}'
        
        # Prepare email content
        context = {
            'registration': registration,
            'event': registration.event,
            'profile_url': registration.get_profile_url(),
        }
        
        html_message = render_to_string('events/emails/registration_approved.html', context)
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[registration.email],
        )
        email.content_subtype = 'html'
        
        # Start attachment generation in background
        attachment_thread = self.generate_attachments_async(registration)
        
        # Send email without attachments first (fast)
        try:
            email.send(fail_silently=False)
            print(f"✅ Email sent successfully (without attachments)")
            
            # Wait for attachments (max 10 seconds)
            attachment_thread.join(timeout=10)
            
            # Send follow-up email with attachments if available
            if registration.id in self.attachment_cache:
                attachments = self.attachment_cache[registration.id]
                if attachments:
                    self.send_attachment_email(registration, attachments, reg_type)
                else:
                    print("No attachments generated - skipping follow-up email")
            
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def send_attachment_email(self, registration, attachments, reg_type):
        """Send follow-up email with attachments"""
        try:
            subject = f'{reg_type} दस्तावेज़ - {registration.event.title}'
            
            # Simple attachment email
            body = f"""
            प्रिय {registration.full_name},
            
            आपके अप्रूव्ड पंजीकरण के दस्तावेज़ संलग्न हैं:
            
            """
            
            if 'id_card' in attachments:
                body += "• ID कार्ड\n"
            if 'vehicle_pass' in attachments:
                body += "• वाहन पास\n"
            
            body += f"""
            
            धन्यवाद,
            {registration.event.title} टीम
            """
            
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[registration.email],
            )
            
            # Attach files
            for attachment_type, attachment_info in attachments.items():
                email.attach(
                    attachment_info['filename'],
                    attachment_info['data'],
                    attachment_info['content_type']
                )
            
            email.send(fail_silently=False)
            print(f"✅ Attachment email sent successfully")
            
            # Clear cache
            del self.attachment_cache[registration.id]
            
        except Exception as e:
            print(f"❌ Attachment email failed: {e}")

# Usage example
def send_optimized_email(registration, sent_by_user=None):
    """Optimized email sending function"""
    sender = OptimizedEmailSender()
    return sender.send_optimized_approval_email(registration, sent_by_user)

if __name__ == "__main__":
    print("Optimized Email System Ready")
    print("Features:")
    print("- Instant email sending (no attachments)")
    print("- Background attachment generation")
    print("- Follow-up email with attachments")
    print("- Smart vehicle detection")
    print("- Reduced server load")