import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ContactMappingForm
from ..models import Campaign, CampaignFile, FileRole
from ..services.contact_parsing import parse_contacts_file
from ..services.contacts import persist_recipients
from ..services.files import read_campaign_file, store_campaign_file
from ..services.validation import detect_mapping

_SESSION_PREFIX = "contact_parse"


def _session_key(campaign_id):
    return f"{_SESSION_PREFIX}:{campaign_id}"


def _get_file_record(campaign, request):
    context = request.session.get(_session_key(campaign.id))
    if not context:
        return None
    return CampaignFile.objects.filter(pk=context["file_id"], campaign=campaign).first()


@login_required
def contact_upload(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)

    if request.method == "POST" and request.FILES.get("contacts_file"):
        upload = request.FILES["contacts_file"]
        data = upload.read()
        try:
            parsed = parse_contacts_file(upload.name, data)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("campaigns:contacts", pk=campaign.id)

        upload.seek(0)
        file_record = store_campaign_file(campaign, upload, FileRole.CONTACTS, request.user)
        request.session[_session_key(campaign.id)] = {
            "file_id": str(file_record.id),
            "sheet_names": parsed["sheet_names"],
        }
        messages.success(request, f"Uploaded {upload.name} ({len(parsed['rows'])} rows).")
        return _render_mapping(request, campaign, file_record, parsed)

    # GET: show the most advanced state we have.
    if campaign.recipients.exists():
        return _render_validation(request, campaign)

    file_record = _get_file_record(campaign, request)
    if file_record:
        parsed = parse_contacts_file(file_record.original_filename, read_campaign_file(file_record))
        return _render_mapping(request, campaign, file_record, parsed)

    return render(request, "a_campaigns/contact_upload.html", {"campaign": campaign})


def _render_mapping(request, campaign, file_record, parsed):
    mapping = detect_mapping(parsed["headers"])
    form = ContactMappingForm(
        headers=parsed["headers"], sheet_names=parsed["sheet_names"], initial=mapping
    )
    labels = [("name", "Name"), ("company", "Company"), ("email", "Email"),
              ("secondary email", "Secondary email"), ("role", "Role")]
    mapping_fields = [
        {
            "key": key,
            "label": label,
            "value": form[key].value(),
            "choices": form.fields[key].choices,
        }
        for key, label in labels
    ]
    return render(
        request,
        "a_campaigns/contact_map.html",
        {
            "campaign": campaign,
            "form": form,
            "mapping_fields": mapping_fields,
            "headers": parsed["headers"],
            "sheet_names": parsed["sheet_names"],
            "row_count": len(parsed["rows"]),
        },
    )


@login_required
def contact_map(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    file_record = _get_file_record(campaign, request)
    if not file_record:
        return redirect("campaigns:contacts", pk=campaign.id)

    sheet_names = request.session.get(_session_key(campaign.id), {}).get("sheet_names") or []
    if request.method == "POST":
        form = ContactMappingForm(
            request.POST,
            headers=_headers_for_sheet(file_record, request.POST.get("sheet")),
            sheet_names=sheet_names,
        )
        if form.is_valid():
            sheet_name = form.cleaned_data.get("sheet") or None
            mapping = form.mapping()
            parsed = parse_contacts_file(
                file_record.original_filename,
                read_campaign_file(file_record),
                sheet_name=sheet_name,
            )
            persist_recipients(campaign, parsed["rows"], mapping)
            messages.success(
                request, f"Validated {campaign.recipients.count()} contact rows."
            )
            return redirect("campaigns:contacts", pk=campaign.id)

    return redirect("campaigns:contacts", pk=campaign.id)


def _headers_for_sheet(file_record, sheet_name):
    parsed = parse_contacts_file(
        file_record.original_filename, read_campaign_file(file_record), sheet_name=sheet_name
    )
    return parsed["headers"]


def _render_validation(request, campaign):
    recipients = campaign.recipients.all()
    total = recipients.count()
    summary = {
        "total": total,
        "valid": recipients.filter(validation_status="valid", excluded=False).count(),
        "invalid": recipients.filter(validation_status="invalid", excluded=False).count(),
        "excluded": recipients.filter(excluded=True).count(),
        "with_secondary": sum(1 for r in recipients if r.secondary_emails),
    }
    return render(
        request,
        "a_campaigns/contact_validation.html",
        {"campaign": campaign, "recipients": recipients, "summary": summary},
    )


@login_required
def contact_error_report(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    rows = campaign.recipients.filter(validation_status="invalid")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{campaign.name}-errors.csv"'
    writer = csv.writer(response)
    writer.writerow(["Row", "Name", "Company", "Primary email", "Secondary emails", "Issues", "Excluded"])
    for r in rows:
        writer.writerow(
            [
                r.source_row_number,
                r.full_name,
                r.company,
                r.primary_email,
                "; ".join(r.secondary_emails),
                "; ".join(_issues_for(r)),
                "yes" if r.excluded else "no",
            ]
        )
    return response


def _issues_for(recipient):
    issues = list(recipient.validation_issues)
    if recipient.exclusion_reason and recipient.exclusion_reason not in issues:
        issues.append(recipient.exclusion_reason)
    return issues or ["Invalid or duplicate contact"]
