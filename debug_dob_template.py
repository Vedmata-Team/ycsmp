#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.template import Template, Context

# Get the test user
user = EventRegistration.objects.get(id=3757)
print(f"User: {user.full_name}")
print(f"DOB: {user.date_of_birth}")
print(f"DOB type: {type(user.date_of_birth)}")

# Test template rendering
template_code = "{{ registration.date_of_birth|date:'Y-m-d' }}"
template = Template(template_code)
context = Context({'registration': user})
rendered = template.render(context)

print(f"Template output: '{rendered}'")
print(f"Template output length: {len(rendered)}")

# Test JavaScript template
js_template = "window.USER_DOB = '{{ registration.date_of_birth|date:\"Y-m-d\" }}';"
js_template_obj = Template(js_template)
js_rendered = js_template_obj.render(context)
print(f"JS template output: {js_rendered}")