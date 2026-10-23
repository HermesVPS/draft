from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """Post-login landing page. Campaigns are wired in later phases."""
    request.session["current_view"] = "dashboard:home"
    return render(request, "dashboard/dashboard.html", {"page_title": "Dashboard"})
