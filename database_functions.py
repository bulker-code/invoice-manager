import sqlite3
import csv
import tabulate
import shutil
from datetime import date

def update_count():
    conn=sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients
        SET invoice_count = (
            SELECT COUNT(*) FROM invoices WHERE invoices.client_id = clients.id
        )
    """)
    conn.commit()
    conn.close()

def alter_table():
    conn=sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE invoices ADD COLUMN voided TEXT NOT NULL DEFAULT 0")
    conn.commit()
    conn.close()


def create_tables():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            invoice_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            code TEXT UNIQUE,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0,
            paid_date TEXT,
            voided TEXT NOT NULL DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            item_date TEXT NOT NULL,
            quantity FLOAT NOT NULL,
            rate FLOAT NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        )

    """)
    
    conn.commit()
    conn.close()

def generate_invoice_code(cursor, client_id, invoice_id):
    cursor.execute("SELECT name, invoice_count from clients WHERE id = ?", (client_id,))
    name, count = cursor.fetchone()
    parts = name.split()
    initials = (parts[0][0] + parts[-1][0]).upper()

    new_count = count + 1
    code = f"{str(new_count).zfill(3)}{initials}"

    cursor.execute("UPDATE clients SET invoice_count = ? WHERE id = ?", (new_count, client_id))
    cursor.execute("UPDATE invoices SET code = ? WHERE id = ?", (code, invoice_id))

    
    
def update_invoice_codes(cursor, client_id):
    # get client initials
    cursor.execute("SELECT name FROM clients WHERE id = ?", (client_id,))
    name = cursor.fetchone()[0]
    parts = name.split()
    initials = (parts[0][0] + parts[-1][0]).upper()

    # get all invoices for this client ordered by issue date
    cursor.execute("""
        SELECT id FROM invoices
        WHERE invoices.client_id = ?
        ORDER BY issue_date
    """, (client_id,))
    invoices = cursor.fetchall()

    # renumber sequentially from 1
    for index, inv_id in enumerate(invoices, start=1):
        new_number = index
        
        cursor.execute("UPDATE invoices SET code = ? WHERE id = ?",
            (f'{str(new_number).zfill(3)}{initials}', inv_id[0]),)

def add_client(name, email, phone, address):
    # Open (or create) the database file, and get a connection to it
    conn = sqlite3.connect("invoices.db")

    # Get a cursor — the object we use to actually run commands
    cursor = conn.cursor()

    # Run the SQL insert. The ? marks are placeholders, filled in
    # by the tuple below, in order. This avoids putting raw values
    # directly into the SQL string (safer, and handles quotes/special
    # characters correctly).
    try:
        cursor.execute(
        "INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
        (name, email, phone, address)
        )
        client_id = cursor.lastrowid
        print(f"Added client: {name}, ID: {client_id}")

    except sqlite3.IntegrityError:
        print("A client with this email already exists")

    
    # Actually save the change to the file
    conn.commit()

    # Close the connection, we're done with it
    conn.close()

def remove_client(client_id):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("""
    DELETE from clients
    WHERE clients.id = ?
    """, (client_id,))
    conn.commit()
    conn.close()
    print(f" Client {client_id} has been removed")

def edit_client(client_id, name=None, email=None, phone=None, address=None):
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)
    if address is not None:
        updates.append("address = ?")
        params.append(address)

    if not updates:
        print("Nothing to update")
        return
    params.append(client_id)

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            UPDATE clients
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        conn.commit()
        print(f"Client {client_id} updated")
    except sqlite3.IntegrityError:
        print("A client with this email already exists")
    conn.commit()
    conn.close()


def show_clients():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, address, invoice_count FROM clients ORDER BY id")
    rows = cursor.fetchall()

    headers = ["ID", "Name", "Email", "Phone", "Address", "Inv Count"]
    print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))

def add_invoice_with_items(client_id, issue_date, due_date):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO invoices (client_id, issue_date, due_date, paid) VALUES (?, ?, ?, ?)",
        (client_id, issue_date, due_date, 0)
    )
    invoice_id = cursor.lastrowid
    items_added = 0

    while True:
        description = input("Item description (or blank to finish): ")
        if description == "":
            break
        
        item_date = input("Item date: ")
        quantity = float(input("Quantity/hours: "))
        rate = float(input("Rate: "))
        
        cursor.execute(
            "INSERT INTO invoice_items (invoice_id, description, item_date, quantity, rate) VALUES (?, ?, ?, ?, ?)",
            (invoice_id, description, item_date, quantity, rate)
        )
        items_added += 1

    if items_added == 0:
        conn.rollback()
        conn.close()
        print("No items entered - invoice cancelled, nothing saved")
        return
    
    generate_invoice_code(cursor, client_id, invoice_id)
    
    cursor.execute("SELECT code from invoices WHERE id = ?", (invoice_id,))
    inv_code = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    print(f"Created invoice. id:{invoice_id}, code: {inv_code} ")
    return inv_code

def void_invoice(invoice_code):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE invoices SET voided = 1 WHERE code = ?", (invoice_code,))
    conn.commit()
    conn.close()
    print(f"Invoice {invoice_code} has been voided")

def remove_invoice(invoice_id):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("""
    DELETE from invoices
    WHERE invoices.id = ?
    """, (invoice_id,))
    conn.commit()
    conn.close()
    print(f"Invoice (id:{invoice_id}) has been removed")

def edit_invoice(invoice_code, issue_date=None, due_date=None):
    updates = []
    params = []

    if issue_date is not None:
        updates.append("issue_date = ?")
        params.append(issue_date.isoformat())

    if due_date is not None:
        updates.append("due_date = ?")
        params.append(due_date.isoformat())

    if not updates:
        print("Nothing to update")
        return

    params.append(invoice_code)

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE invoices
        SET {', '.join(updates)}
        WHERE code = ?
    """, params)
    conn.commit()
    conn.close()
    print(f"Invoice {invoice_code} updated")

def edit_invoice_item(item_id, item_date=None, description=None, quantity=None, rate=None):
    updates = []
    params = []

    if item_date is not None:
        updates.append("item_date = ?")
        params.append(item_date.isoformat())

    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if quantity is not None:
        updates.append("quantity = ?")
        params.append(quantity)

    if rate is not None:
        updates.append("rate = ?")
        params.append(rate)
  
    if not updates:
        print("Nothing to update")
        return

    params.append(item_id)

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE invoice_items
        SET {', '.join(updates)}
        WHERE id = ?
    """, params)
    conn.commit()
    conn.close()
    print(f"Invoice {item_id} updated")
          
def show_all_invoices():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT invoices.id, invoices.code, clients.name, invoices.issue_date, SUM(invoice_items.quantity * invoice_items.rate) AS total, invoices.paid, invoices.paid_date, invoices.voided
    FROM invoices
    JOIN clients ON invoices.client_id = clients.id
    JOIN invoice_items ON invoice_items.invoice_id = invoices.id
    WHERE invoices.voided = 0
    GROUP BY invoices.id
    ORDER BY invoices.due_date
    """
    )
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    headers = ["ID", "INV Code", "Client Name", "Issue Date", "TOTAL", "Paid", "Paid_Date", "voided"]
    print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))

def show_unpaid_invoices(overdue=False):
    conditions = ["invoices.paid = 0", "invoices.voided = 0"]
    if overdue:
        conditions.append("invoices.due_date < date('now')")
    where_clause = "WHERE " + " AND ".join(conditions)
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT invoices.id, invoices.code, clients.name, invoices.due_date, SUM(invoice_items.quantity * invoice_items.rate) AS total
    FROM invoices
    JOIN clients ON invoices.client_id = clients.id
    JOIN invoice_items ON invoice_items.invoice_id = invoices.id
    {where_clause}
    GROUP BY invoices.id
    ORDER BY invoices.due_date
    """
    )
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    headers = ["ID", "CODE", "Client Name", "Due Date", "TOTAL"]
    print(tabulate.tabulate(rows, headers=headers, tablefmt='grid'))

def show_invoice_items(invoice_code):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT invoices.id, invoices.code, invoice_items.id, clients.name, invoices.due_date, invoice_items.description, invoice_items.quantity, invoice_items.rate, (invoice_items.quantity * invoice_items.rate) as subtotal
    FROM invoices
    JOIN clients ON clients.id = invoices.client_id
    JOIN invoice_items ON invoice_items.invoice_id = invoices.id
    WHERE invoices.code = ?
    """, (invoice_code,))

    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    headers = ["ID", "Invoice CODE", "Item ID", "Client Name", "Invoice Due Date", "Item Description", "Quantity", "Rate", "SUBTOTAL"]
    print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))

def mark_paid(invoice_code, paid_date):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE invoices SET paid = 1, paid_date = ? WHERE code = ?",
        (paid_date, invoice_code)
    )
    conn.commit()
    conn.close()
    print(f"Marked invoice {invoice_code} as paid")

def total_unpaid(client_id, overdue=False):
    conditions = ["invoices.paid = 0", "invoices.voided = 0", "invoices.client_id = ?"]
    if overdue:
        conditions.append("invoices.due_date < date('now')")
    where_clause = "WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT clients.name from clients where clients.id = ?", (client_id,))
    client_name = cursor.fetchone()[0]
    cursor.execute(f"""
    SELECT SUM(invoice_items.quantity * invoice_items.rate) AS total_revenue
    FROM invoices
    JOIN invoice_items ON invoice_items.invoice_id = invoices.id
    JOIN clients ON clients.id = invoices.client_id
    {where_clause}
    """, (client_id,))
    result = cursor.fetchone()[0]
    total_unpaid = result if result is not None else 0
    conn.commit()
    conn.close()
    print(f"Total of unpaid invoices for client {client_id} ({client_name}) is: ${total_unpaid}")

def get_invoice_data(invoice_code):
    conn =sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT clients.name, clients.address, clients.email, clients.phone, invoices.code, invoices.issue_date, invoices.due_date,  invoice_items.item_date, invoice_items.description, invoice_items.quantity, invoice_items.rate, invoice_items.rate * invoice_items.quantity AS subtotal
                   FROM invoices
                   JOIN clients ON clients.id = invoices.client_id
                   JOIN invoice_items ON invoice_items.invoice_id = invoices.id
                   WHERE invoices.code = ?
                   """, (invoice_code, ))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data


def backup_database():
    backup_name = f"invoices_backup_{date.today().isoformat()}.db"
    shutil.copy2("invoices.db", backup_name)
    print(f"Backed up to {backup_name}")

def export_csv(issue_from=None, issue_to=None, paid_from=None, paid_to=None, paid_only=False, unpaid_only=False, client_id=None):
    conditions = ['invoices.voided = 0']
    params = []

    if paid_only:
        conditions.append("invoices.paid = 1")
    elif unpaid_only:
        conditions.append("invoices.paid = 0")

    if client_id is not None:
        conditions.append("invoices.client_id = ?")
        params.append(client_id)
    
    if issue_from is not None and issue_to is not None:
        conditions.append("invoices.issue_date BETWEEN ? AND ?")
        params.append(issue_from.isoformat())
        params.append(issue_to.isoformat())

    if paid_from is not None and paid_to is not None:
        conditions.append("invoices.paid_date BETWEEN ? AND ?")
        params.append(paid_from.isoformat())
        params.append(paid_to.isoformat())

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT invoices.code, clients.name, clients.email, invoices.issue_date, invoices.due_date, SUM(invoice_items.quantity * invoice_items.rate) AS total, invoices.paid, invoices.paid_date
        FROM invoices
        JOIN clients ON invoices.client_id = clients.id
        JOIN invoice_items ON invoice_items.invoice_id = invoices.id
        {where_clause}
        GROUP BY invoices.id
        ORDER BY invoices.due_date
    """, params)
    rows = cursor.fetchall()
    total = sum(row[5] for row in rows)
    export_name = f'revenue_export_{date.today().isoformat()}.csv'
    try:
        with open(export_name, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
    
            headers = ['Code', 'Name', 'Email', 'Issue Date', 'Due Date', 'Amount', 'Paid', "Paid Date"] 
            writer.writerow(headers)

            # 5. Write all the data rows
            writer.writerows(rows)
            writer.writerow(['','','','', total])
            print("Export complete!")

    except PermissionError:
        print(f"{export_name} is open in another program — close it and try again.")
    conn.commit()
    conn.close()