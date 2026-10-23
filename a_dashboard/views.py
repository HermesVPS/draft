from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from a_campaigns.models import Campaign


@login_required
def dashboard(request):
    """Post-login landing page showing quick actions and recent campaigns."""
    request.session["current_view"] = "dashboard:home"
    recent = Campaign.objects.filter(owner=request.user)[:5]
    context = {
        "page_title": "Dashboard",
        "recent_campaigns": recent,
    }
    return render(request, "dashboard/dashboard.html", context)
