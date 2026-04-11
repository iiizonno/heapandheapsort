import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from managers.expense_manager import ExpenseManager
from gui.add_window import TransactionFormWindow


class MainWindow(tk.Tk):
    """
    Main application window for the Personal Expense Tracker.

    Provides the primary user interface with filtering controls, transaction table,
    summary displays, and action buttons for managing financial transactions.
    """

    def __init__(self, manager: ExpenseManager):
        """
        Initialize the main application window.

        Args:
            manager: The ExpenseManager instance containing business logic and data
        """
        super().__init__()
        self.title("Personal Expense Tracker")
        self.state('zoomed')  # Maximize window on startup
        self.manager = manager

        # Initialize filter controls
        self.filter_year_all = tk.BooleanVar(value=True)
        self.filter_year = tk.IntVar(value=2026)
        self.filter_month = tk.StringVar(value="All")
        self.filter_category = tk.StringVar(value="All")
        self.search_var = tk.StringVar()

        self.create_layout()
        # Defer refresh until window is fully mapped to ensure Treeview is ready
        self.bind("<Map>", lambda e: self.refresh_all())

    def create_layout(self) -> None:
        """
        Create and arrange all GUI components in the main window.
        
        Builds three main sections: financial summary, filter controls, and transaction table.
        """
        # Financial summary display
        summary_frame = tk.Frame(self, relief="raised", bd=2)
        summary_frame.pack(fill="x", padx=10, pady=8)

        self.income_label = tk.Label(summary_frame, text="Income: $0.00", font=("Arial", 12, "bold"), fg="green")
        self.expense_label = tk.Label(summary_frame, text="Expense: $0.00", font=("Arial", 12, "bold"), fg="red")
        self.net_label = tk.Label(summary_frame, text="Net: $0.00", font=("Arial", 14, "bold"))
        self.remaining_label = tk.Label(summary_frame, text="Remaining Budget: $0.00", font=("Arial", 12, "bold"), fg="blue")

        for i, lbl in enumerate([self.income_label, self.expense_label, self.net_label, self.remaining_label]):
            lbl.grid(row=0, column=i, padx=20, pady=8)

        # Filter controls section
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Year filter controls
        tk.Label(filter_frame, text="Year:").pack(side="left")
        year_all_check = tk.Checkbutton(filter_frame, text="All", variable=self.filter_year_all, 
                                       command=self._on_year_all_toggle)
        year_all_check.pack(side="left", padx=5)
        
        self.year_spinbox = tk.Spinbox(filter_frame, from_=2020, to=2030, textvariable=self.filter_year, 
                                      width=6, state='disabled' if self.filter_year_all.get() else 'normal')
        self.year_spinbox.pack(side="left", padx=5)
        self.year_spinbox.bind("<KeyRelease>", lambda e: self.refresh_all())
        self.year_spinbox.bind("<<Increment>>", lambda e: self.refresh_all())
        self.year_spinbox.bind("<<Decrement>>", lambda e: self.refresh_all())

        # Month filter
        tk.Label(filter_frame, text="Month:").pack(side="left", padx=(15, 5))
        month_combo = ttk.Combobox(filter_frame, textvariable=self.filter_month, width=8, state='readonly')
        month_combo['values'] = ["All"] + [calendar.month_abbr[m] for m in range(1, 13)]
        month_combo.pack(side="left", padx=5)
        month_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())

        # Category filter
        tk.Label(filter_frame, text="Category:").pack(side="left", padx=(15, 5))
        cat_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category, width=15, state='readonly')
        cat_combo['values'] = ["All"] + [c.name for c in self.manager.categories]
        cat_combo.pack(side="left", padx=5)
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())

        # Search/keyword filter
        tk.Label(filter_frame, text="Search:").pack(side="left", padx=(15, 5))
        tk.Entry(filter_frame, textvariable=self.search_var, width=20).pack(side="left", padx=5)
        self.search_var.trace("w", lambda *args: self.refresh_all())

        # Main body: left side transaction list, right side income/expense charts
        body_frame = tk.Frame(self)
        body_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Transaction table/Treeview on the left
        tree_frame = tk.Frame(body_frame)
        tree_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Charts on the right
        chart_panel = tk.Frame(body_frame, width=420)
        chart_panel.pack(side="left", fill="y")
        chart_panel.pack_propagate(False)

        expense_chart_frame = tk.Frame(chart_panel, relief="groove", bd=2)
        expense_chart_frame.pack(fill="x", pady=(0, 5), padx=5)
        tk.Label(expense_chart_frame, text="Expense Categories", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6, 0))
        self.expense_chart_canvas = tk.Canvas(expense_chart_frame, height=220, bg="white", highlightthickness=0)
        self.expense_chart_canvas.pack(fill="x", padx=8, pady=8)
        self.expense_chart_canvas.bind("<Configure>", lambda e: self.draw_pie_charts())

        income_chart_frame = tk.Frame(chart_panel, relief="groove", bd=2)
        income_chart_frame.pack(fill="x", padx=5)
        tk.Label(income_chart_frame, text="Income Categories", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6, 0))
        self.income_chart_canvas = tk.Canvas(income_chart_frame, height=220, bg="white", highlightthickness=0)
        self.income_chart_canvas.pack(fill="x", padx=8, pady=8)
        self.income_chart_canvas.bind("<Configure>", lambda e: self.draw_pie_charts())

        columns = ("id", "date", "type", "category", "amount", "description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("description", text="Description")

        # Configure column widths and alignment
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=90)
        self.tree.column("type", width=70)
        self.tree.column("category", width=100)
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("description", width=250)

        # Add vertical scrollbar to Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Add", command=self.open_add_window, bg="#4CAF50", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", command=self.open_edit_window, bg="#2196F3", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_selected, bg="#f44336", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Set Budget", command=self.open_budget_window, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Report", command=self.show_report, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_all, width=10).pack(side="left", padx=5)

    def _get_month_number(self) -> Optional[str]:
        """
        Convert abbreviated month name to month number string.

        Returns:
            Month number as "01"-"12" string, or None if "All" is selected
        """
        month_name = self.filter_month.get()
        if month_name == "All":
            return None
        try:
            return str(list(calendar.month_abbr).index(month_name)).zfill(2)
        except ValueError:
            return None

    def refresh_table(self) -> None:
        """
        Update the transaction table with current filter settings.
        
        Clears all existing table entries and repopulates with filtered transactions.
        """
        # Clear existing table entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        trans_list = self.manager.get_transactions(
            filter_year=None if self.filter_year_all.get() else str(self.filter_year.get()),
            filter_month=self._get_month_number(),
            filter_category=None if self.filter_category.get() == "All" else self.filter_category.get(),
            search_keyword=self.search_var.get().strip() or None
        )

        for trans in trans_list:
            self.tree.insert("", "end", iid=str(trans.id), values=(
                trans.id,
                trans.date.strftime("%Y-%m-%d"),
                trans.type.capitalize(),
                trans.category,
                f"${trans.amount:,.2f}",
                trans.description
            ))

    def update_summary(self) -> None:
        """
        Update the financial summary labels with current filter settings.
        """
        summary = self.manager.get_monthly_summary(
            None if self.filter_year_all.get() else str(self.filter_year.get()),
            self._get_month_number()
        )
        self.income_label.config(text=f"Income: ${summary['total_income']:,.2f}")
        self.expense_label.config(text=f"Expense: ${summary['total_expense']:,.2f}")
        self.net_label.config(text=f"Net: ${summary['net']:,.2f}")
        self.remaining_label.config(text=f"Remaining Budget: ${self.manager.get_total_remaining_budget(
            None if self.filter_year_all.get() else str(self.filter_year.get()),
            self._get_month_number()
        ):,.2f}")

    def _on_year_all_toggle(self):
        """
        Handle the "All years" checkbox toggle.

        Enables/disables the year spinbox based on checkbox state and refreshes the display.
        """
        if self.filter_year_all.get():
            self.year_spinbox.config(state='disabled')
        else:
            self.year_spinbox.config(state='normal')
        self.refresh_all()

    def refresh_all(self) -> None:
        """
        Refresh the transaction table, summary displays, and both pie charts.
        """
        self.refresh_table()
        self.update_summary()
        self.draw_pie_charts()
        self.update_idletasks()  # Ensure GUI updates are processed

    def draw_pie_charts(self) -> None:
        """
        Draw income and expense pie charts on the right-side canvases.
        """
        if hasattr(self, "expense_chart_canvas"):
            self.draw_pie_chart(
                self.expense_chart_canvas,
                "Expense Categories",
                "expense"
            )
        if hasattr(self, "income_chart_canvas"):
            self.draw_pie_chart(
                self.income_chart_canvas,
                "Income Categories",
                "income"
            )

    def draw_pie_chart(self, canvas: tk.Canvas, title: str, trans_type: str) -> None:
        """
        Draw a single pie chart for the given transaction type.
        """
        canvas.delete("all")
        width = max(canvas.winfo_width(), 360)
        height = max(canvas.winfo_height(), 220)
        center_x = width * 0.18 if width > 420 else width * 0.24
        center_y = height / 2 + 12
        radius = min(width * 0.18, height * 0.34)

        chart_data = self.manager.get_pie_chart_data(
            trans_type,
            None if self.filter_year_all.get() else str(self.filter_year.get()),
            self._get_month_number()
        )

        if not chart_data["labels"]:
            canvas.create_text(
                width / 2,
                height / 2,
                text=f"No {trans_type} data available.",
                fill="#555555",
                font=("Arial", 11, "italic")
            )
            return

        total = sum(chart_data["sizes"])
        start_angle = 0
        legend_x = width * 0.56 if width > 420 else width * 0.55
        legend_y = 20
        legend_line_height = 18

        for label, size, color in zip(chart_data["labels"], chart_data["sizes"], chart_data["colors"]):
            extent = size / total * 360 if total > 0 else 0
            canvas.create_arc(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start=start_angle,
                extent=extent,
                fill=color,
                outline="white"
            )
            start_angle += extent
            canvas.create_rectangle(
                legend_x,
                legend_y,
                legend_x + 12,
                legend_y + 12,
                fill=color,
                outline="#444444"
            )
            canvas.create_text(
                legend_x + 18,
                legend_y + 6,
                anchor="w",
                text=f"{label}: ${size:,.2f}",
                fill="#333333",
                font=("Arial", 9)
            )
            legend_y += legend_line_height

        canvas.create_text(
            center_x,
            14,
            text=title,
            fill="#222222",
            font=("Arial", 11, "bold")
        )

    def open_add_window(self) -> None:
        """
        Open the add transaction window.
        """
        TransactionFormWindow(self, self.manager, self.refresh_all)

    def open_edit_window(self):
        """
        Open the edit transaction window for the selected transaction.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to edit.")
            return
        trans_id = int(selected[0])
        for t in self.manager.transactions:
            if t.id == trans_id:
                TransactionFormWindow(self, self.manager, self.refresh_all, transaction=t)
                return
        messagebox.showerror("Error", "Transaction not found.")

    def delete_selected(self):
        """
        Delete the selected transaction after user confirmation.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete selected transaction?"):
            trans_id = int(selected[0])
            if self.manager.delete_transaction(trans_id):
                self.refresh_all()
                messagebox.showinfo("Deleted", "Transaction deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete transaction.")

    def open_budget_window(self):
        """
        Open a modal window to set monthly budget limits for categories.
        """
        budget_win = tk.Toplevel(self)
        budget_win.title("Set Monthly Budget")
        budget_win.geometry("300x200")

        tk.Label(budget_win, text="Category:").pack(pady=5)
        cat_combo = ttk.Combobox(budget_win, values=[c.name for c in self.manager.categories], state='readonly')
        cat_combo.pack()

        tk.Label(budget_win, text="Limit ($):").pack(pady=5)
        limit_entry = tk.Entry(budget_win)
        limit_entry.pack()

        def save_budget():
            try:
                cat = cat_combo.get()
                amt = float(limit_entry.get())
                self.manager.budget.set_limit(cat, amt)
                messagebox.showinfo("Success", f"Budget for {cat} set to ${amt:,.2f}")
                budget_win.destroy()
                self.refresh_all()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")

        tk.Button(budget_win, text="Save", command=save_budget).pack(pady=10)

    def show_report(self):
        year = "All" if self.filter_year_all.get() else str(self.filter_year.get())
        month = self.filter_month.get()
        if year != "All" and month != "All":
            period = f"{year}-{month}"
        elif year != "All":
            period = year
        elif month != "All":
            period = f"Month {month}"
        else:
            period = "All Time"

        summary = self.manager.get_monthly_summary(
            None if year == "All" else year,
            self._get_month_number()
        )
        report = f"""Report – {period}
Income: ${summary['total_income']:,.2f}
Expense: ${summary['total_expense']:,.2f}
Net Balance: ${summary['net']:,.2f}
"""
        messagebox.showinfo("Report", report)