# INVOICE CLI

A command line invoice management tool for small businesses. Manage clients, create and send professional PDF invoices, track payments, and calculate revenue of a given time period. Built as a personal project to manage invoicing for my support work business.

## Features

- **Client management** - Add and remove clients with automatic unique client ids to keep them distinct and separate
- **Line-item invoices** - Line items with a date, quantity, and rate
- **PDF generation** - Professionally formatted PDFs generated automatically when an invoice is added
- **Invoice codes** - Unique codes generated based on client name and number of invoices sent to them
- **Revenue filtering by date range** - Calculates revenue of invoices paid within date range (inclusive)
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
python invoice_cli.py add-invoice-with-items --client-id 1 --issue-date 2026-07-09 --no-pdf
```
<img width="2000" height="2588" alt="image" src="https://github.com/user-attachments/assets/f26f447d-9dc1-4e67-b0a5-d8657bec1f89" />

**remove-invoice** - Removes invoice by code

```
python invoice_cli.py remove-invoice --invoice-code 001JS
```

**show-all-invoices** - Shows tables of all invoices

```
python invoice_cli.py show-all-invoices
```
```
+--------+----------+------------+------------+---------+------+------------+
| Inv ID | INV Code | Client     | Issue Date | Total   | Paid | Paid Date  |
+========+==========+============+============+=========+======+============+
|      1 | 001JS    | Jane Smith | 2026-06-01 | $120.00 |    1 | 2026-06-05 |
+--------+----------+------------+------------+---------+------+------------+
|      2 | 001BJ    | Bob Jones  | 2026-06-15 | $135.00 |    0 |            |
+--------+----------+------------+------------+---------+------+------------+
```
**show-unpaid-invoices** - Shows table of all unpaid invoices

```
python invoice_cli.py show-unpaid-invoices
```
```
+--------+------------+------------+---------+
| Inv ID | Client     | Due Date   | Total   |
+========+============+============+=========+
|      2 | Bob Jones  | 2026-06-22 | $135.00 |
+--------+------------+------------+---------+
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

**calculate-revenue** - Shows total revenue of invoices paid between selected dates

```
python invoice_cli.py calculate-revenue --from-date 2025-07-01 --to-date 2026-06-30
```

**total-unpaid** - Shows total of unpaid invoices for a client

```
python invoice_cli.py total-unpaid --client-id 1
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
