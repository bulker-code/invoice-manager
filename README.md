# INVOICE CLI

Built for my support work business, so I could check whether an invoice has been paid, and what's on it, without digging back through the original PDF every time.

A command line invoice management tool for small businesses. Manage clients, create and send professional PDF invoices, track payments, and calculate revenue of a given time period. Built as a personal project to manage invoicing for my support work business.

## Features

- **Client management** - Add, edit, and remove clients with automatic unique client ids to keep them distinct and separate
- **Line-item invoices** - Line items with a date, quantity, and rate, editable after creation
- **PDF generation** - Professionally formatted PDFs generated automatically when an invoice is added
- **Invoice codes** - Permanent unique codes generated per client, based on client initials and a running count - never reused or renumbered, even if an invoice is later voided
- **Voiding, not deleting** - Cancel an invoice without losing its number or record; permanent deletion is still available separately
- **Overdue tracking** - Filter unpaid invoices and totals down to only what's actually past its due date
- **CSV export** - Export invoices to CSV for accountant handoff or reporting, filterable by client, paid status, issue date, and paid date
- **Financial year folder organisation** - Auto-creates folder path in destination to categorise invoices by financial year


## Requirements
- Python 3.8+

## Installation

```bash
git clone https://github.com/bulker-code/invoice_cli.git
cd invoice_cli
pip install reportlab tabulate
```
1. Copy `config_example.py` to `config.py`
2. Fill in your business details in `config.py`
3. Run `python invoice_cli.py --help` to verify the installation

## Usage

**add-client** - Add a new client

```
python invoice_cli.py add-client --name "Jane Smith" --email jane@example.com --phone 0412345678 --address "123 Main St"
```

**remove-client** - Remove a client and all associated invoices

```
python invoice_cli.py remove-client --client-id 1
```

**edit-client** - Updates a client's name, email, phone, and/or address. Only the fields you pass are changed.

```
python invoice_cli.py edit-client --client-id 1 --phone 0499999999
```

**show-clients** - Shows table of all current clients

```
python invoice_cli.py show-clients
```
```
+----+------------+-------------------+-------------+---------------------------+
| ID | Name       | Email             | Phone       | Address                   |
+====+============+===================+=============+===========================+
|  1 | Jane Smith | jane@example.com  | 0412345678  | 123 Main St, Brisbane     |
+----+------------+-------------------+-------------+---------------------------+
|  2 | Bob Jones  | bob@example.com   | 0423456789  | 456 Example Rd, Sydney    |
+----+------------+-------------------+-------------+---------------------------+
```

**add-invoice-with-items** - Create a new invoice interactively, prompting for line items. PDF is automatically generated and saved on completion, unless `--no-pdf` is passed.

```
python invoice_cli.py add-invoice-with-items --client-id 1 --issue-date 2026-07-09
```
<img width="2000" height="2588" alt="image" src="https://github.com/user-attachments/assets/f26f447d-9dc1-4e67-b0a5-d8657bec1f89" />

**remove-invoice** - Permanently deletes an invoice by its database id (see the ID column in `show-invoices`). Prefer `void-invoice` unless you actually want the row gone.

```
python invoice_cli.py remove-invoice --invoice-id 5
```

**void-invoice** - Marks an invoice as voided/cancelled instead of deleting it, so its code is never reused. Voided invoices are excluded from `show-invoices`, `total-unpaid`, and `export-csv`.

```
python invoice_cli.py void-invoice --invoice-code 001JS
```

**edit-invoice** - Updates the issue date and/or due date on an existing invoice. Only the fields you pass are changed.

```
python invoice_cli.py edit-invoice --invoice-code 001JS --issue-date 2026-07-10 --due-date 2026-07-17
```

**edit-invoice-item** - Updates a single line item's date, description, quantity, or rate. Find the item's id first with `show-invoice-items`. Only the fields you pass are changed.

```
python invoice_cli.py edit-invoice-item --item-id 12 --quantity 3 --rate 55
```

**show-invoices** - Shows a table of non-voided invoices. With no flags, shows everything. Filter down using any combination of:
- `--client-id` - only invoices for one client
- `--paid` - only paid invoices
- `--unpaid` - only unpaid invoices
- `--overdue` - only unpaid invoices past their due date (does not require `--unpaid` flag)

```
python invoice_cli.py show-invoices --client-id 2 --overdue
```
```
+--------+----------+------------+------------+------------+---------+------+------------+
| Inv ID | CODE     | Client     | Issue Date | Due Date   | Total   | Paid | Paid Date  |
+========+==========+============+============+============+=========+======+============+
|      1 | 001JS    | Jane Smith | 2026-06-01 | 2026-06-08 | $120.00 |    1 | 2026-06-05 |
+--------+----------+------------+------------+------------+---------+------+------------+
|      2 | 001BJ    | Bob Jones  | 2026-06-15 | 2026-06-22 | $135.00 |    0 |            |
+--------+----------+------------+------------+------------+---------+------+------------+
```

**show-invoice-items** - Display all line items for a specific invoice

```
python invoice_cli.py show-invoice-items --invoice-code 001JS
```
```
+--------+------------+-----------------+---------------------+----------+--------+---------+
| Inv ID | Client     | Due Date        | Item Description    | Quantity | Rate   | Subtotal|
+========+============+=================+=====================+==========+========+=========+
|      1 | Jane Smith | 2026-06-08      | Tutoring Session    |     2.00 | $50.00 | $100.00 |
+--------+------------+-----------------+---------------------+----------+--------+---------+
|      1 | Jane Smith | 2026-06-08      | Travel Reimbursement|     1.00 | $20.00 |  $20.00 |
+--------+------------+-----------------+---------------------+----------+--------+---------+
```

**mark-paid** - Mark an invoice as paid using its invoice code and the date payment was received

```
python invoice_cli.py mark-paid --invoice-code 001JS --paid-date 2026-07-09
```

**total-unpaid** - Shows total of unpaid, non-voided invoices for a client. Add `--overdue` to only total invoices past their due date.

```
python invoice_cli.py total-unpaid --client-id 1
python invoice_cli.py total-unpaid --client-id 1 --overdue
```

**generate-pdf** - Generates a new pdf for an existing invoice

```
python invoice_cli.py generate-pdf --invoice-code 001JS
```

**backup-database** - Creates a backup copy of the SQLite database labelled with today's date

```
python invoice_cli.py backup-database
```

**export-csv** - Export a csv to show record of invoices
Exports invoices to a CSV file for reporting or handing off to an accountant — e.g. everything paid within a financial year. With no flags, exports every invoice. Filter down using any combination of:
- `--paid-only` / `--unpaid-only` - only paid or only unpaid invoices
- `--client-id` - only invoices for one client
- `--issue-from` / `--issue-to` - invoices issued within a date range
- `--paid-from` / `--paid-to` - invoices paid within a date range

```
python invoice_cli.py export-csv --paid-only --paid-from 2025-07-01 --paid-to 2026-06-30
```


## File structure
- **invoice_cli.py** - primary python file holding cli commands. Run this file to use the tool.
- **database_functions.py** - stores all functions where direct interaction with the SQLite database is required
- **pdf_generator.py** - holds function required to generate pdfs
- **config.py** - created by user to store business details. Present in gitignore.
- **config_example.py** - shows example format for config.py
- **INV_FIRST_LAST** - example client invoice folders
