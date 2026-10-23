from django import forms

from .models import Campaign, EmailTemplate
from .services.validation import CANONICAL_COLUMNS


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ["name", "subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": "Subject (supports [Name], [Company]...)"}),
            "body": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault("class", "input input-bordered w-full")
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "textarea textarea-bordered w-full")


class CampaignForm(forms.ModelForm):
    """Campaign setup form (wizard step 1)."""

    class Meta:
        model = Campaign
        fields = [
            "name",
            "outlook_connection_label",
            "destination_folder_name",
            "subject_original",
            "body_original",
            "batch_size",
            "safe_punctuation_enabled",
            "date_review_required",
            "attachments_required",
            "notes",
        ]
        widgets = {
            "subject_original": forms.TextInput(attrs={"placeholder": "Email subject (supports [Name], [Company]...)"}),
            "body_original": forms.Textarea(attrs={"rows": 10, "placeholder": "Email body. First line may be SUBJECT: when pasting a template."}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "batch_size": forms.NumberInput(attrs={"min": 1, "max": 12}),
        }
        labels = {
            "subject_original": "Subject",
            "body_original": "Body",
            "outlook_connection_label": "Outlook account",
            "destination_folder_name": "Destination Drafts subfolder",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault("class", "input input-bordered w-full")
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "textarea textarea-bordered w-full")
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "checkbox checkbox-primary")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "select select-bordered w-full")


class ContactMappingForm(forms.Form):
    """Maps canonical columns to the uploaded file's headers (wizard step 2)."""

    sheet = forms.ChoiceField(required=False)

    def __init__(self, *args, headers=None, sheet_names=None, **kwargs):
        super().__init__(*args, **kwargs)
        headers = headers or []
        sheet_names = sheet_names or []
        choices = [("", "— not present —")] + [(h, h) for h in headers if h]

        self.fields["sheet"].choices = [(s, s) for s in sheet_names]
        self.fields["sheet"].required = len(sheet_names) > 1
        if sheet_names:
            self.fields["sheet"].initial = sheet_names[0]

        for canonical in CANONICAL_COLUMNS:
            self.fields[canonical] = forms.ChoiceField(
                choices=choices, required=False, label=canonical.title()
            )

    def clean(self):
        cleaned = super().clean()
        # Require the three mandatory columns to be mapped.
        missing = [
            label
            for key, label in [("name", "Name"), ("company", "Company"), ("email", "Email")]
            if not cleaned.get(key)
        ]
        if missing:
            raise forms.ValidationError(f"Map these required columns: {', '.join(missing)}.")
        return cleaned

    def mapping(self):
        """Return ``{canonical: header}`` from the cleaned fields."""
        return {
            key: self.cleaned_data[key]
            for key in CANONICAL_COLUMNS
            if self.cleaned_data.get(key)
        }
