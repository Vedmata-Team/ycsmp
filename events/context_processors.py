from .models_warning import SiteWarning

def site_warnings(request):
    """Add active site warnings to all templates"""
    warnings = SiteWarning.objects.filter(is_active=True)
    return {'site_warnings': warnings}