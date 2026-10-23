import io

from django.test import SimpleTestCase
from openpyxl import Workbook

from a_campaigns.services.contact_parsing import (
    is_lock_file,
    parse_contacts_file,
    parse_xlsx_bytes,
)


def make_xlsx(rows, sheet_name=None, extra_sheet=None):
    wb = Workbook()
    ws = wb.active
    if sheet_name:
        ws.title = sheet_name
    for row in rows:
        ws.append(row)
    if extra_sheet is not None:
        ws2 = wb.create_sheet(extra_sheet)
        ws2.append(["Unrelated"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class ParseXlsxTests(SimpleTestCase):
    def test_parses_first_sheet(self):
        data = make_xlsx([["Name", "Company", "Email"], ["Alice", "Acme", "alice@x.com"]])
        parsed = parse_xlsx_bytes(data)
        self.assertEqual(parsed["headers"], ["Name", "Company", "Email"])
        self.assertEqual(len(parsed["rows"]), 1)
        self.assertEqual(parsed["rows"][0]["Email"], "alice@x.com")

    def test_sheet_selection(self):
        data = make_xlsx([["Name", "Email"], ["Bob", "bob@x.com"]], sheet_name="Contacts", extra_sheet="Notes")
        parsed = parse_xlsx_bytes(data, sheet_name="Contacts")
        self.assertEqual(parsed["sheet_names"], ["Contacts", "Notes"])
        self.assertEqual(parsed["headers"], ["Name", "Email"])

    def test_empty_rows_dropped(self):
        data = make_xlsx([["Name", "Email"], ["Bob", "bob@x.com"], [None, None]])
        parsed = parse_xlsx_bytes(data)
        self.assertEqual(len(parsed["rows"]), 1)

    def test_preserves_email_as_text(self):
        # Emails that could be mistaken for numbers must stay text.
        data = make_xlsx([["Email"], ["12345@example.com"]])
        parsed = parse_xlsx_bytes(data)
        self.assertEqual(parsed["rows"][0]["Email"], "12345@example.com")


class DispatchTests(SimpleTestCase):
    def test_lock_file_detection(self):
        self.assertTrue(is_lock_file("~$contacts.xlsx"))
        self.assertFalse(is_lock_file("contacts.xlsx"))

    def test_csv_dispatch(self):
        parsed = parse_contacts_file("list.csv", b"name,email\nAlice,alice@x.com\n")
        self.assertEqual(parsed["rows"][0]["email"], "alice@x.com")

    def test_xlsx_dispatch(self):
        data = make_xlsx([["Name", "Email"], ["Alice", "alice@x.com"]])
        parsed = parse_contacts_file("list.xlsx", data)
        self.assertEqual(parsed["rows"][0]["Name"], "Alice")

    def test_unsupported_type(self):
        with self.assertRaises(ValueError):
            parse_contacts_file("list.txt", b"whatever")
