from datetime import date, timedelta, datetime 
import argparse
from database_functions import create_tables, add_client, add_invoice_with_items, \
remove_client, void_invoice, mark_paid, show_clients, show_all_invoices, show_unpaid_invoices, \
backup_database, show_invoice_items, total_unpaid, export_csv, remove_invoice
from pdf_generator import generate_invoice_pdf

if __name__ == "__main__":
    create_tables()
        
parser = argparse.ArgumentParser(description="Invoice CLI")
subparsers = parser.add_subparsers(dest="command")

#add-client
p = subparsers.add_parser("add-client")
p.add_argument("--name", required=True)
p.add_argument("--email", required=True)
p.add_argument("--phone", required=True)
p.add_argument("--address", required=True)

#remove-client
p = subparsers.add_parser("remove-client")
p.add_argument("--client-id", type=int, required=True)

#show-clients (no extra args needed)
p = subparsers.add_parser("show-clients")

#add-invoice-with-items
p = subparsers.add_parser("add-invoice-with-items")
p.add_argument("--client-id", type=int, required=True)
p.add_argument("--issue-date", type=date.fromisoformat, required = True)
p.add_argument("--no-pdf", action="store_true")

#remove-invoice
p=subparsers.add_parser("remove-invoice")
p.add_argument("--invoice-code", required=True)
#void-invoice
p=subparsers.add_parser("void-invoice")
p.add_argument("--invoice-code", required=True)

#show-all-invoices
# eventually change to show invoices and filter based on client/s, dates, etc
p = subparsers.add_parser("show-all-invoices")

#show-unpaid-invoices
p = subparsers.add_parser("show-unpaid-invoices")

#show-invoice-items
p = subparsers.add_parser("show-invoice-items")
p.add_argument("--invoice-code", required=True)

#mark-paid
p = subparsers.add_parser("mark-paid")
p.add_argument("--invoice-code", type=str, required=True)
p.add_argument("--paid-date", type=date.fromisoformat, required=True)

#total-unpaid
p = subparsers.add_parser("total-unpaid")
p.add_argument("--client-id", type=int, required=True)

#calculate-revenue
p = subparsers.add_parser("calculate-revenue")
p.add_argument("--from-date", type=date.fromisoformat, required=True)
p.add_argument("--to-date", type=date.fromisoformat , required=True)

#generate-pdf
p = subparsers.add_parser("generate-pdf")
p.add_argument("--invoice-code", required=True)

#backup-database
p = subparsers.add_parser("backup-database")

#export-csv
p = subparsers.add_parser("export-csv")
p.add_argument("--paid-only", action="store_true")
p.add_argument("--unpaid-only", action="store_true")
p.add_argument("--client-id", type=int)
p.add_argument("--issue-from", type=date.fromisoformat)
p.add_argument("--issue-to", type=date.fromisoformat)
p.add_argument("--paid-from", type=date.fromisoformat)
p.add_argument("--paid-to", type=date.fromisoformat)

args = parser.parse_args()

if args.command == "add-client":
    add_client(args.name, args.email, args.phone, args.address)

elif args.command == "remove-client":
    remove_client(args.client_id)

elif args.command == "show-clients":
    show_clients()

elif args.command == "add-invoice-with-items":
    issue_date = args.issue_date    
    due_date = (issue_date + timedelta(days=7)).isoformat()
    invoice_code = add_invoice_with_items(args.client_id, issue_date, due_date)
    if invoice_code and not args.no_pdf:
        generate_invoice_pdf(invoice_code)

elif args.command == "remove-invoice":
    remove_invoice(args.invoice_code)

elif args.command == "void-invoice":
    void_invoice(args.invoice_code)

elif args.command == "show-all-invoices":
    show_all_invoices()
   
elif args.command == "show-unpaid-invoices":
    show_unpaid_invoices()

elif args.command == "show-invoice-items":
    show_invoice_items(args.invoice_code)

elif args.command == "mark-paid":
    mark_paid(args.invoice_code, args.paid_date.isoformat())

elif args.command == "total-unpaid":
    total_unpaid(args.client_id)

elif args.command == "generate-pdf":
    generate_invoice_pdf(args.invoice_code)

elif args.command == "backup-database":
    backup_database()

elif args.command == "export-csv":
    export_csv(issue_from=args.issue_from, issue_to=args.issue_to, paid_from=args.paid_from, paid_to=args.paid_to, paid_only=args.paid_only, unpaid_only=args.unpaid_only, client_id=args.client_id)