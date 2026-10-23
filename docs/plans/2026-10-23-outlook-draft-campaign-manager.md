# Outlook Draft Campaign Manager — Standalone Django Build Plan

> **For Hermes:** Implement directly, phase by phase, committing at phase
> boundaries. Most phases touch the same app files sequentially, so delegation
> would fight over files. TDD for all pure logic.

**Goal:** Port the ChatGPT Sites "Outlook Draft Campaign Manager" MVP into the
`HermesVPS/draft` Django repo as a standalone, reusable Django app (`a_campaigns`)
that creates and organises personalised Outlook drafts via Microsoft Graph
(Entra OAuth) — never sending email — with full feature parity to the MVP,
including the unsubscribe/suppression mailbox sync.

**Architecture:** A single reusable Django app with a thin provider abstraction
(`EmailProvider` ABC) so Microsoft Graph ships now and a Gmail adapter can be
added later without touching the campaign workflow. Pure domain logic is ported
verbatim from the MVP's `lib/campaign.mjs` into Python and covered by tests. The
processing engine runs in a background thread with durable per-recipient
progress in Postgres/SQLite, honouring Outlook throttling (`Retry-After`),
idempotency, and reconciliation of uncertain results.

**Tech Stack:** Django 6.0, django-allauth (existing auth), MSAL (Python),
openpyxl (.xlsx), mammoth (Python, .docx→HTML), bleach (HTML sanitisation),
HTMX + Alpine.js + Tailwind v4/DaisyUI (existing frontend), uv.

---

## Source of truth

The MVP lives in Drive at `outlook Draft creator/outlook-draft-campaign-manager-tracking/`.
Key files (read locally at `/opt/data/mvp-src/`):

- `prompt.txt` — the full spec (20 acceptance test cases).
- `issues report.txt` — real-world findings (throttling 62s, uncertain results,
  drafts stuck in root Drafts, smart-punctuation corruption, 3 accounts).
- `db/schema.ts` + `drizzle/*.sql` — the D1 schema (8 tables).
- `lib/campaign.mjs` — pure domain logic (parse, validate, personalise, state
  machine, idempotency, readiness).
- `app/api/microsoft/draft/route.ts` — the direct MS Graph draft pipeline
  (ensureFolder → create → attach → move → verify).
- `app/api/microsoft/config/route.ts` — client/tenant/scopes config.
- `app/api/unsubscribes/route.ts` — shared-mailbox suppression sync.
- `app/api/templates/word/route.ts` — .docx (mammoth) import.
- `app/api/campaigns/route.ts`, `app/api/files/route.ts` — CRUD + uploads.
- `lib/server-email-html.ts` — sanitise-html allowlist config.

---

## Data model (Django ORM mapping)

App `a_campaigns`, models split across a `models/` package (Ryan's convention):

- `Campaign` — owner FK(User), name, status, outlook_connection_label,
  destination_folder_name/id, subject_original/outgoing, body_original/outgoing,
  batch_size (default 8), safe_punctuation_enabled (default True),
  date_review_required, attachments_required, notes, created/updated/started/
  completed/cancelled_at. Index (owner, status).
- `CampaignRecipient` — campaign FK, source_row_number, full_name,
  salutation_name, company, role, primary_email, normalized_address_set,
  secondary_emails_json (JSON), custom_fields_json (JSON), validation_status,
  processing_status, excluded (bool), exclusion_reason, subject_hash,
  attachment_set_hash, outlook_draft_id, destination_folder_id, attempt_count,
  retry_after, last_error, created/started/completed_at.
  UniqueConstraint(campaign, source_row_number); Index(campaign, processing_status).
- `CampaignFile` — campaign FK, file_role (contacts|template|attachment),
  original_filename, content_type, size_bytes, storage_key, checksum,
  uploaded_by FK, created_at. Unique storage_key.
- `CampaignRun` — campaign FK, status, authorised_by FK, authorised_at,
  total_recipients, completed/failed/reconciliation_count, current_batch,
  last_progress_at, next_retry_at, started/completed_at.
- `AuditEvent` — campaign FK, recipient FK (null), run FK (null), user FK,
  event_type, event_summary, provider_request_id, created_at.
- `EmailTemplate` — owner FK, name, subject, body, timestamps. Unique (owner, name).
- `SuppressionEntry` — owner FK, email, display_name, source_mailbox,
  source_folder, source_message_id, source_received_at, timestamps.
  Unique (owner, email), Unique (owner, source_message_id).
- `MailboxSyncState` — owner FK, mailbox, folder_path, last_checked_at,
  last_message_count, last_imported_count, last_error, timestamps.
  Unique (owner, mailbox, folder_path).
- `MicrosoftAccount` — owner FK, provider label, msal account id, mail/UPN,
  encrypted refresh token, connected_at. Unique (owner, msal account id).
  (New — the standalone app stores its OWN refresh token, encrypted, instead of
  relying on a ChatGPT connector.)

Processing status values (recipient): `pending, creating_draft, attaching,
moving, verifying, complete, failed, waiting_for_retry, reconciliation_required,
cancelled, excluded`.
Campaign status values: `draft, ready, running, waiting, completed, failed,
cancelled`.
Run status values: `running, paused, waiting, completed, failed, cancelled`.

---

## Phases

### Phase 0 — Environment & scaffold

**Goal:** A clean, runnable baseline with all deps and a post-login dashboard.

**Why first:** Every later phase needs `uv run` + a landing page to render
against. Renaming now avoids "bitesize"/"P5JS" branding drift proliferating.

- Rename project: `pyproject.toml` name → `draft`, update `package.json` name.
- `uv add msal openpyxl mammoth bleach`
- Add `.env.example` documenting every `config()` key (SECRET_KEY, DEBUG,
  UV_LINK_MODE, MS_GRAPH_CLIENT_ID/SECRET/TENANT_ID, MS_GRAPH_SCOPES,
  TOKEN_ENCRYPTION_KEY, SUPPRESSION_MAILBOX, SUPPRESSION_FOLDER, DATABASE_URL,
  MEDIA settings).
- Settings: media storage (`MEDIA_ROOT`/`MEDIA_URL`), `ALLOWED_HOSTS` from env,
  optional Postgres via `DATABASE_URL` (env-driven switching pattern), app in
  `INSTALLED_APPS`.
- Create `a_dashboard` app: post-login landing, `LOGIN_REDIRECT_URL = '/dashboard/'`,
  conditional root redirect (fixes the `/ → login → /` loop, pitfall #10).
- Verify: `uv run python manage.py check`, runserver, login → dashboard.

### Phase 1 — Domain logic library (TDD)

**Goal:** Port `lib/campaign.mjs` to pure Python with full test coverage.

**Why first:** These functions are the spec's heart (20 acceptance cases) and
are pure/testable with no Django or network dependencies. Getting them right
first de-risks everything downstream.

Files: `a_campaigns/services/` — `text_utils.py` (parse_text_template,
safe_punctuation, safe_punctuation_html, escape_html, html_to_text),
`personalisation.py` (salutation_name, split_emails, is_email, find_placeholders,
personalise, personalise_html), `dates.py` (find_numbered_dates),
`validation.py` (validate_contacts, detect_mapping, campaign_readiness_issues),
`state.py` (recipient_transition, idempotency_key).

Port the acceptance cases from `prompt.txt` as pytest tests (leading blank lines,
smart quotes, "Dr Rowena B." → "Rowena", primary+secondary To line, duplicate
primary, secondary-as-primary duplicate, missing fields, invalid email, unknown
placeholder, exact dates vs general wording).

### Phase 2 — Data models (migrations + admin)

**Goal:** Django models mirroring the schema above, migrations, admin.

- Create `a_campaigns/models/` package with the models + `__init__.py`.
- Register all models in admin (list_display, filters, search).
- `makemigrations` + `migrate`; verify tables and constraints.

### Phase 3 — Contact upload & validation

**Goal:** Accept `.xlsx`/`.csv`, auto-detect columns, map, validate, persist.

- `services/contact_parsing.py`: `parse_csv` (Python csv), `parse_xlsx`
  (openpyxl — first sheet default, list sheets, ignore `~$` lock files, preserve
  emails as text), `detect_mapping`.
- View: upload → store file (CampaignFile role=contacts) → parse → column
  mapping form → validate → persist CampaignRecipients with validation_status.
- Render validation summary (valid/missing/invalid/duplicate/repeated/blank/
  excluded) + downloadable error report (CSV).

### Phase 4 — Templates & email HTML

**Goal:** Paste/upload/edit subject+body, reusable templates, `.docx` import,
sanitisation, preview with personalisation.

- `services/email_html.py`: port the sanitise-html allowlist to bleach (same
  tags/attributes/styles/schemes as `server-email-html.ts`).
- `services/word_import.py`: mammoth `.docx` → HTML → extract SUBJECT: line →
  sanitise (mirror `templates/word/route.ts`).
- `EmailTemplate` CRUD (save/load reusable templates).
- Placeholder validation (error on unknown placeholder); salutation override.

### Phase 5 — Microsoft Graph provider + abstraction

**Goal:** Server-side Entra OAuth + the draft pipeline, behind an `EmailProvider`
ABC with a Gmail stub.

- `services/provider/base.py`: `EmailProvider` ABC (get_profile, list_folders,
  ensure_folder, create_draft, attach_file, move_draft, verify_draft,
  list_mail_folders, list_messages — the last two for the suppression sync).
- `services/provider/microsoft_graph.py`: MSAL confidential client; auth-code
  flow (connect + callback views); store refresh token encrypted (Fernet, key
  from `TOKEN_ENCRYPTION_KEY`); port the draft pipeline verbatim from
  `microsoft/draft/route.ts` (ensureFolder nested under Drafts → POST /me/messages
  → attach PDFs ≤3MB/≤10MB total → move → verify subject/recipients/attachments).
- `services/provider/gmail.py`: `NotImplementedError` stub (Gmail adapter slot).
- Scopes from `MS_GRAPH_SCOPES` (default includes `Mail.ReadWrite` and
  `Mail.ReadWrite.Shared` for the shared mailbox).
- Verify with a fixture (fake transport) — no live drafts in dev.

### Phase 6 — Processing workflow

**Goal:** Durable, resumable, throttled, idempotent batch runner.

- `services/processing.py`: background `threading.Thread` runner following the
  skill's pattern (catch-all except → FAILED via `.filter().update()`).
- `services/state.py` recipient_transition drives each recipient through
  creating_draft → attaching → moving → verifying → complete.
- Freeze recipient set + outgoing template into a `CampaignRun` at start.
- Batch loop (sequential, size = campaign.batch_size); on 429 store
  `retry_after`/`next_retry_at` → `waiting_for_retry`; honour `Retry-After`.
- Idempotency: one draft record per (campaign, recipient); `reconciliation_required`
  on uncertain results; never auto-replay an uncertain write.
- Actions: start (with double-click/two-tab guard), resume, cancel, retry-failed,
  reconcile; progress saved after every recipient; HTMX polling endpoint.

### Phase 7 — Campaign UI (5-step wizard) + history + results

**Goal:** The full user-facing workflow in Django templates + HTMX + Alpine.

- 5 steps: Setup → Contact validation → Draft preview → Confirm & create →
  Results/history. Visible step indicator (Alpine).
- Campaign setup fields per spec (name, account, folder w/ new-or-existing +
  duplicate-folder guard, uploads, subject/body, attachments, batch size,
  Outlook-safe punctuation, notes).
- Preview (first / a secondary / last recipient; per-recipient preview);
  Outlook-safe transformed copy shown; date-review findings (non-blocking unless
  "Require date approval").
- Confirmation screen with the exact confirmation checkbox; Start disabled until
  checked; "no emails will be sent" statement; account+folder shown near Start.
- History list (open / duplicate / delete-with-confirmation / CSV export) and
  results page (recipient table, status filters, CSV export).

### Phase 8 — Suppression/unsubscribe sync

**Goal:** Port the shared-mailbox UNSUBSCRIBE scan.

- `services/suppression.py`: list shared-mailbox folders (`/users/{mailbox}/
  mailFolders`), find `UNSUBSCRIBE`, list messages, extract forwarded `From:
  Name <email>` from body, upsert `SuppressionEntry` (dedupe by email + message
  id), update `MailboxSyncState`.
- Settings `SUPPRESSION_MAILBOX`/`SUPPRESSION_FOLDER` (defaults
  support@proactivetraining.com.au / UNSUBSCRIBE).

### Phase 9 — Hardening, tests, docs, deploy notes

**Goal:** Ship-ready.

- Full `pytest` + `manage.py test` pass; `manage.py check`.
- `.env.example` complete; README (setup, Entra app registration steps, scopes).
- Rollback/deploy notes (Postgres, gunicorn single-worker for the background
  thread, Celery as the scale-up path, R2/S3 for media via django-storages).

---

## Key decisions & rationale

- **Provider abstraction now (Graph + Gmail stub):** matches the recorded
  direction (support M365 + Google bulk drafting behind one interface). Gmail
  adapter is a follow-up; the campaign engine is provider-agnostic.
- **Background thread, not Celery:** matches the MVP's "no permanent worker"
  constraint and the skill's proven pattern; single-process deploy. Celery is the
  documented scale-up.
- **Encrypted refresh token in `MicrosoftAccount`:** standalone app owns its
  OAuth state (the MVP leaned on ChatGPT's connector token store).
- **bleach over nh3:** closest parity to the MVP's granular `sanitize-html`
  style allowlist. Tradeoff noted (bleach is in maintenance mode; nh3 is the
  modern alt if we drop granular style filtering).
- **openpyxl for .xlsx, Python `mammoth` for .docx:** exact parity with the
  MVP's `xlsx` and `mammoth` (Node) deps, but native Python.
