from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CampaignForm
from ..models import Campaign, CampaignRecipient


@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(owner=request.user)
    return render(request, "a_campaigns/campaign_list.html", {"campaigns": campaigns})


@login_required
def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.owner = request.user
            campaign.save()
            return redirect("campaigns:contacts", pk=campaign.id)
    else:
        form = CampaignForm()
    return render(request, "a_campaigns/campaign_form.html", {"form": form, "creating": True})


@login_required
def campaign_update(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect("campaigns:contacts", pk=campaign.id)
    else:
        form = CampaignForm(instance=campaign)
    return render(request, "a_campaigns/campaign_form.html", {"form": form, "campaign": campaign})


@login_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    if request.method == "POST":
        name = campaign.name
        campaign.delete()
        messages.success(
            request,
            f"Campaign '{name}' deleted. No Outlook drafts were deleted.",
        )
        return redirect("campaigns:list")
    return render(request, "a_campaigns/campaign_confirm_delete.html", {"campaign": campaign})


@login_required
def campaign_duplicate(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    duplicate = Campaign.objects.create(
        owner=request.user,
        name=f"{campaign.name} (copy)",
        outlook_connection_label=campaign.outlook_connection_label,
        destination_folder_name=campaign.destination_folder_name,
        subject_original=campaign.subject_original,
        subject_outgoing=campaign.subject_outgoing,
        body_original=campaign.body_original,
        body_outgoing=campaign.body_outgoing,
        batch_size=campaign.batch_size,
        safe_punctuation_enabled=campaign.safe_punctuation_enabled,
        date_review_required=campaign.date_review_required,
        attachments_required=campaign.attachments_required,
        notes=campaign.notes,
    )
    for recipient in campaign.recipients.all():
        CampaignRecipient.objects.create(
            campaign=duplicate,
            source_row_number=recipient.source_row_number,
            full_name=recipient.full_name,
            salutation_name=recipient.salutation_name,
            company=recipient.company,
            role=recipient.role,
            primary_email=recipient.primary_email,
            normalized_address_set=recipient.normalized_address_set,
            secondary_emails_json=recipient.secondary_emails_json,
            custom_fields_json=recipient.custom_fields_json,
        )
    messages.success(request, f"Duplicated '{campaign.name}' as a new editable campaign.")
    return redirect("campaigns:contacts", pk=duplicate.id)
