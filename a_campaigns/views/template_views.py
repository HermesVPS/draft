from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import EmailTemplateForm
from ..models import Campaign, EmailTemplate
from ..services.text_utils import parse_text_template
from ..services.word_import import import_docx


@login_required
def template_list(request):
    templates = EmailTemplate.objects.filter(owner=request.user)
    return render(request, "a_campaigns/template_list.html", {"templates": templates})


@login_required
@require_POST
def template_save(request):
    form = EmailTemplateForm(request.POST)
    if form.is_valid():
        template = form.save(commit=False)
        template.owner = request.user
        template.save()
        messages.success(request, f"Saved template '{template.name}'.")
    else:
        messages.error(request, "Could not save template. Check the required fields.")
    next_url = request.POST.get("next") or "campaigns:templates"
    return redirect(next_url)


@login_required
@require_POST
def template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk, owner=request.user)
    name = template.name
    template.delete()
    messages.success(request, f"Deleted template '{name}'.")
    return redirect("campaigns:templates")


@login_required
@require_POST
def template_apply(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk, owner=request.user)
    campaign_id = request.POST.get("campaign_id")
    campaign = get_object_or_404(Campaign, pk=campaign_id, owner=request.user)
    campaign.subject_original = template.subject
    campaign.body_original = template.body
    campaign.save()
    messages.success(request, f"Loaded template '{template.name}' into the campaign.")
    return redirect("campaigns:update", pk=campaign.id)


@login_required
@require_POST
def template_import(request):
    """Import a .txt or .docx template and return subject/body as JSON.

    Used by the campaign setup step to pre-fill the subject/body fields.
    """
    upload = request.FILES.get("template")
    if not upload:
        return JsonResponse({"error": "Choose a template file."}, status=400)

    name = (upload.name or "").lower()
    try:
        if name.endswith(".txt"):
            parsed = parse_text_template(upload.read().decode("utf-8-sig", errors="replace"))
            return JsonResponse(
                {"subject": parsed["subject"], "body": parsed["body"], "format": "text"}
            )
        if name.endswith(".docx"):
            result = import_docx(upload.read())
            return JsonResponse(
                {
                    "subject": result["subject"],
                    "body": result["body"],
                    "format": result["format"],
                    "messages": result["messages"],
                }
            )
        return JsonResponse({"error": "Upload a .txt or .docx template."}, status=400)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
