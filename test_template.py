import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cargo_ms.settings')
django.setup()

from django.template.loader import render_to_string

try:
    html = render_to_string('auth/login.html', {})
    print("✓ Template rendered successfully!")
    print(f"✓ Template length: {len(html)} chars")
except Exception as e:
    print(f"✗ Template error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
