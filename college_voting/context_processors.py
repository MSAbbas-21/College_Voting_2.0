"""
Global context processors for college_voting.
"""

def global_settings(request):
    """Provide site-wide common variables."""
    return {
        'SITE_NAME': 'Apex College Voting Portal',
        'COLLEGE_NAME': 'Apex Institute of Technology & Management',
        'ACADEMIC_YEAR': '2026-2027',
    }
