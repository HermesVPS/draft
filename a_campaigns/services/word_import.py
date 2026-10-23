"""Word (.docx) template import, ported from the MVP's mammoth-based route.

The MVP used mammoth (Node); we use the official mammoth Python package.
"""

import io

import mammoth

from .email_html import extract_subject_from_html, plain_text, sanitize_email_html

DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_WORD_TEMPLATE = 5 * 1024 * 1024


def convert_docx_to_html(data):
    """Convert .docx bytes to HTML using mammoth.

    Returns ``(html, messages)`` where messages is a list of warning strings.
    """
    result = mammoth.convert_to_html(
        io.BytesIO(data),
        include_default_style_map=True,
        ignore_empty_paragraphs=False,
        convert_image=mammoth.images.img_element(lambda image: {"src": ""}),
        style_map="p[style-name='Email Subject'] => p:fresh",
    )
    return result.value, list(result.messages)


def import_docx(data):
    """Convert and sanitise a .docx template into ``{subject, body, format}``.

    Raises ``ValueError`` when the document has no usable email body.
    """
    raw_html, messages = convert_docx_to_html(data)
    sanitized = sanitize_email_html(raw_html)
    parsed = extract_subject_from_html(sanitized)
    if not plain_text(parsed["body"]):
        raise ValueError("The Word document did not contain an email body.")
    return {"subject": parsed["subject"], "body": parsed["body"], "format": "html", "messages": messages}
