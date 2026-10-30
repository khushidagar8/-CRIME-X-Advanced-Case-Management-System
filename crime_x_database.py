
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ==========================================
# CRIME-X ADVANCED CASE MANAGEMENT SYSTEM
# ==========================================

DB_NAME = "crime_x_database.db"

BG = "#101827"
PANEL = "#1B293B"
CARD = "#24364B"
WHITE = "#FFFFFF"
BLUE = "#2589FF"
GREEN = "#16A085"
RED = "#E74C3C"
YELLOW = "#F39C12"


# ==========================================
# DATABASE
# ==========================================

def connect_db():
    return sqlite3.connect(DB_NAME)


def create_database():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE,
            title TEXT,
            category TEXT,
            location TEXT,
            status TEXT,
            priority TEXT,
            investigator TEXT,
            description TEXT,
            created_at TEXT
        )
    """)

    con.commit()
    con.close()


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("CRIME-X | Advanced Case Management")
root.geometry("1200x750")
root.minsize(1000, 650)
root.configure(bg=BG)


# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def get_cases(search=""):
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, case_number, title, category,
        location, status, priority, investigator, created_at
        FROM cases
        WHERE case_number LIKE ?
        OR title LIKE ?
        OR category LIKE ?
        OR location LIKE ?
        ORDER BY id DESC
    """, tuple(["%" + search + "%"] * 4))

    data = cur.fetchall()
    con.close()
    return data


def refresh_table():
    for item in tree.get_children():
        tree.delete(item)

    records = get_cases(search_var.get())

    for record in records:
        tree.insert("", "end", values=record)

    update_dashboard()


def update_dashboard():
    con = connect_db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM cases")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cases WHERE status='Open'")
    opened = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cases WHERE status='Under Investigation'")
    investigation = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cases WHERE status='Closed'")
    closed = cur.fetchone()[0]

    con.close()

    total_label.config(text=str(total))
    open_label.config(text=str(opened))
    investigation_label.config(text=str(investigation))
    closed_label.config(text=str(closed))


# ==========================================
# SELECT CASE
# ==========================================

def selected_case():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a case first."
        )
        return None

    values = tree.item(selected[0], "values")
    return values[0]


# ==========================================
# ADD CASE
# ==========================================

def add_case():
    case_window = tk.Toplevel(root)
    case_window.title("Add New Case")
    case_window.geometry("500x650")
    case_window.configure(bg=PANEL)
    case_window.resizable(False, False)

    tk.Label(
        case_window,
        text="REGISTER NEW CASE",
        font=("Arial", 19, "bold"),
        fg=BLUE,
        bg=PANEL
    ).pack(pady=20)

    fields = {}

    def create_field(label, default=""):
        tk.Label(
            case_window,
            text=label,
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=PANEL
        ).pack(anchor="w", padx=35, pady=(8, 3))

        entry = tk.Entry(
            case_window,
            font=("Arial", 11),
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat"
        )
        entry.pack(fill="x", padx=35, ipady=7)

        entry.insert(0, default)
        fields[label] = entry

    create_field("Case Number")
    create_field("Case Title")
    create_field("Category")
    create_field("Location")
    create_field("Investigator")

    def create_dropdown(label, options):
        tk.Label(
            case_window,
            text=label,
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=PANEL
        ).pack(anchor="w", padx=35, pady=(8, 3))

        combo = ttk.Combobox(
            case_window,
            values=options,
            state="readonly",
            font=("Arial", 10)
        )
        combo.pack(fill="x", padx=35, ipady=5)
        combo.current(0)
        fields[label] = combo

    create_dropdown(
        "Status",
        ["Open", "Under Investigation", "Closed"]
    )

    create_dropdown(
        "Priority",
        ["Low", "Medium", "High", "Critical"]
    )

    tk.Label(
        case_window,
        text="Case Description",
        font=("Arial", 10, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(anchor="w", padx=35, pady=(8, 3))

    description = tk.Text(
        case_window,
        height=4,
        bg=CARD,
        fg=WHITE,
        insertbackground=WHITE,
        font=("Arial", 10),
        relief="flat"
    )
    description.pack(fill="x", padx=35)

    def save_case():
        values = {
            key: widget.get().strip()
            for key, widget in fields.items()
        }

        desc = description.get("1.0", "end").strip()

        required = [
            "Case Number",
            "Case Title",
            "Category",
            "Location",
            "Investigator"
        ]

        for field in required:
            if not values[field]:
                messagebox.showwarning(
                    "Missing Information",
                    field + " is required."
                )
                return

        con = connect_db()
        cur = con.cursor()

        try:
            cur.execute("""
                INSERT INTO cases (
                    case_number, title, category, location,
                    status, priority, investigator,
                    description, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                values["Case Number"],
                values["Case Title"],
                values["Category"],
                values["Location"],
                values["Status"],
                values["Priority"],
                values["Investigator"],
                desc,
                datetime.now().strftime("%d-%m-%Y %H:%M")
            ))

            con.commit()
            messagebox.showinfo(
                "Success",
                "New case registered successfully!"
            )

            case_window.destroy()
            refresh_table()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate Case",
                "This Case Number already exists."
            )

        finally:
            con.close()

    tk.Button(
        case_window,
        text="SAVE CASE",
        command=save_case,
        bg=GREEN,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(fill="x", padx=35, pady=20, ipady=10)


# ==========================================
# VIEW CASE DETAILS
# ==========================================

def view_case_details(case_id):
    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM cases WHERE id=?",
        (case_id,)
    )

    case = cur.fetchone()
    con.close()

    if not case:
        messagebox.showerror("Error", "Case not found.")
        return

    win = tk.Toplevel(root)
    win.title("Case Details")
    win.geometry("550x600")
    win.configure(bg=PANEL)

    tk.Label(
        win,
        text="CASE INFORMATION",
        font=("Arial", 20, "bold"),
        fg=BLUE,
        bg=PANEL
    ).pack(pady=20)

    labels = [
        "Database ID",
        "Case Number",
        "Title",
        "Category",
        "Location",
        "Status",
        "Priority",
        "Investigator",
        "Description",
        "Created At"
    ]

    for label, value in zip(labels, case):
        tk.Label(
            win,
            text=label + ": " + str(value),
            font=("Arial", 10),
            fg=WHITE,
            bg=PANEL,
            anchor="w",
            wraplength=470,
            justify="left"
        ).pack(fill="x", padx=30, pady=7)


# ==========================================
# EDIT CASE
# ==========================================

def edit_case(case_id):
    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM cases WHERE id=?",
        (case_id,)
    )
    case = cur.fetchone()
    con.close()

    if not case:
        messagebox.showerror("Error", "Case not found.")
        return

    win = tk.Toplevel(root)
    win.title("Edit Case")
    win.geometry("500x680")
    win.configure(bg=PANEL)

    tk.Label(
        win,
        text="UPDATE CASE",
        font=("Arial", 20, "bold"),
        fg=BLUE,
        bg=PANEL
    ).pack(pady=15)

    entries = {}

    def field(label, value):
        tk.Label(
            win,
            text=label,
            fg=WHITE,
            bg=PANEL
        ).pack(anchor="w", padx=30, pady=(7, 2))

        e = tk.Entry(
            win,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            font=("Arial", 10),
            relief="flat"
        )
        e.pack(fill="x", padx=30, ipady=6)
        e.insert(0, str(value))
        entries[label] = e

    field("Case Number", case[1])
    field("Case Title", case[2])
    field("Category", case[3])
    field("Location", case[4])

    for label, options, current in [
        ("Status", ["Open", "Under Investigation", "Closed"], case[5]),
        ("Priority", ["Low", "Medium", "High", "Critical"], case[6])
    ]:
        tk.Label(
            win,
            text=label,
            fg=WHITE,
            bg=PANEL
        ).pack(anchor="w", padx=30, pady=(7, 2))

        combo = ttk.Combobox(
            win,
            values=options,
            state="readonly"
        )
        combo.pack(fill="x", padx=30, ipady=5)
        combo.set(current)
        entries[label] = combo

    field("Investigator", case[7])

    tk.Label(
        win,
        text="Description",
        fg=WHITE,
        bg=PANEL
    ).pack(anchor="w", padx=30, pady=(7, 2))

    desc = tk.Text(
        win,
        height=4,
        bg=CARD,
        fg=WHITE,
        insertbackground=WHITE
    )
    desc.pack(fill="x", padx=30)
    desc.insert("1.0", case[8])

    def update_case():
        values = [
            entries["Case Number"].get().strip(),
            entries["Case Title"].get().strip(),
            entries["Category"].get().strip(),
            entries["Location"].get().strip(),
            entries["Status"].get(),
            entries["Priority"].get(),
            entries["Investigator"].get().strip(),
            desc.get("1.0", "end").strip()
        ]

        if not all(values):
            messagebox.showwarning(
                "Missing Data",
                "Please fill all fields."
            )
            return

        con = connect_db()
        cur = con.cursor()

        try:
            cur.execute("""
                UPDATE cases
                SET case_number=?, title=?, category=?,
                location=?, status=?, priority=?,
                investigator=?, description=?
                WHERE id=?
            """, (*values, case_id))

            con.commit()

            messagebox.showinfo(
                "Updated",
                "Case updated successfully!"
            )

            win.destroy()
            refresh_table()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate",
                "This Case Number already exists."
            )

        finally:
            con.close()

    tk.Button(
        win,
        text="UPDATE CASE",
        command=update_case,
        bg=GREEN,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat"
    ).pack(fill="x", padx=30, pady=20, ipady=8)


# ==========================================
# DELETE CASE
# ==========================================

def delete_case(case_id):
    answer = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this case?"
    )

    if not answer:
        return

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM cases WHERE id=?",
        (case_id,)
    )

    con.commit()
    con.close()

    messagebox.showinfo(
        "Deleted",
        "Case deleted successfully."
    )

    refresh_table()


# ==========================================
# BUTTON ACTIONS
# ==========================================

def open_selected(action):
    case_id = selected_case()

    if case_id is None:
        return

    if action == "view":
        view_case_details(case_id)

    elif action == "edit":
        edit_case(case_id)

    elif action == "delete":
        delete_case(case_id)


def search_cases():
    refresh_table()


def clear_search():
    search_var.set("")
    refresh_table()


# ==========================================
# HEADER
# ==========================================

header = tk.Frame(root, bg="#0B1220", height=85)
header.pack(fill="x")

tk.Label(
    header,
    text="CRIME-X",
    font=("Arial", 27, "bold"),
    fg=BLUE,
    bg="#0B1220"
).pack(side="left", padx=30, pady=18)

tk.Label(
    header,
    text="ADVANCED CASE MANAGEMENT SYSTEM",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg="#0B1220"
).pack(side="left", padx=15)


# ==========================================
# DASHBOARD CARDS
# ==========================================

dashboard = tk.Frame(root, bg=BG)
dashboard.pack(fill="x", padx=20, pady=20)


def dashboard_card(parent, title, color):
    card = tk.Frame(
        parent,
        bg=PANEL,
        width=240,
        height=95
    )
    card.pack(side="left", expand=True, fill="x", padx=7)
    card.pack_propagate(False)

    tk.Label(
        card,
        text=title,
        font=("Arial", 10, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(pady=(12, 3))

    number = tk.Label(
        card,
        text="0",
        font=("Arial", 23, "bold"),
        fg=color,
        bg=PANEL
    )
    number.pack()

    return number


total_label = dashboard_card(
    dashboard, "TOTAL CASES", BLUE
)

open_label = dashboard_card(
    dashboard, "OPEN CASES", YELLOW
)

investigation_label = dashboard_card(
    dashboard, "UNDER INVESTIGATION", GREEN
)

closed_label = dashboard_card(
    dashboard, "CLOSED CASES", RED
)


# ==========================================
# SEARCH BAR
# ==========================================

search_frame = tk.Frame(root, bg=BG)
search_frame.pack(fill="x", padx=30, pady=10)

search_var = tk.StringVar()

search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    font=("Arial", 11),
    bg=CARD,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat"
)

search_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=10
)

search_entry.insert(0, "")

tk.Button(
    search_frame,
    text="SEARCH",
    command=search_cases,
    bg=BLUE,
    fg=WHITE,
    relief="flat",
    font=("Arial", 10, "bold")
).pack(side="left", padx=8, ipadx=15, ipady=7)

tk.Button(
    search_frame,
    text="CLEAR",
    command=clear_search,
    bg=CARD,
    fg=WHITE,
    relief="flat"
).pack(side="left", padx=5, ipadx=12, ipady=7)


# ==========================================
# CASE TABLE
# ==========================================

table_frame = tk.Frame(root, bg=PANEL)
table_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=10
)

columns = (
    "ID",
    "Case Number",
    "Title",
    "Category",
    "Location",
    "Status",
    "Priority",
    "Investigator",
    "Created"
)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=PANEL,
    foreground=WHITE,
    fieldbackground=PANEL,
    rowheight=32,
    font=("Arial", 9)
)

style.configure(
    "Treeview.Heading",
    background="#263C55",
    foreground=WHITE,
    font=("Arial", 9, "bold")
)

style.map(
    "Treeview",
    background=[("selected", BLUE)],
    foreground=[("selected", WHITE)]
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=115, anchor="center")

tree.column("ID", width=45)
tree.column("Title", width=150)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# ==========================================
# ACTION BUTTONS
# ==========================================

buttons = tk.Frame(root, bg=BG)
buttons.pack(fill="x", padx=25, pady=15)


def make_button(parent, text, command, color):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=10
    )


make_button(
    buttons,
    "VIEW DETAILS",
    lambda: open_selected("view"),
    BLUE
).pack(side="left", padx=5)

make_button(
    buttons,
    "EDIT CASE",
    lambda: open_selected("edit"),
    GREEN
).pack(side="left", padx=5)

make_button(
    buttons,
    "DELETE CASE",
    lambda: open_selected("delete"),
    RED
).pack(side="left", padx=5)

make_button(
    buttons,
    "+ ADD NEW CASE",
    add_case,
    "#8E44AD"
).pack(side="right", padx=5)


# ==========================================
# FOOTER
# ==========================================

footer = tk.Label(
    root,
    text="CRIME-X | Advanced Case Management System | Python + SQLite",
    bg="#0B1220",
    fg="#AAB7C4",
    font=("Arial", 9)
)

footer.pack(fill="x", pady=(5, 0), ipady=10)


# ==========================================
# START APPLICATION
# ==========================================

create_database()
refresh_table()

root.mainloop()
