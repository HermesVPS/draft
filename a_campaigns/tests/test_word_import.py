import io
import zipfile

from django.test import SimpleTestCase

from a_campaigns.services.word_import import import_docx


def make_docx(paragraphs):
    """Build a minimal valid .docx in memory."""
    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    document += '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
    for text in paragraphs:
        document += f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
    document += "</w:body></w:document>"

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)
    return buf.getvalue()


class ImportDocxTests(SimpleTestCase):
    def test_import_with_subject(self):
        data = make_docx(["SUBJECT: Campaign subject", "Hello [Name],", "Regards"])
        result = import_docx(data)
        self.assertEqual(result["subject"], "Campaign subject")
        self.assertEqual(result["format"], "html")
        self.assertIn("Hello [Name]", result["body"])

    def test_import_without_subject(self):
        data = make_docx(["Just a body line"])
        result = import_docx(data)
        self.assertEqual(result["subject"], "")
        self.assertIn("Just a body line", result["body"])

    def test_empty_document_raises(self):
        data = make_docx([])
        with self.assertRaises(ValueError):
            import_docx(data)
