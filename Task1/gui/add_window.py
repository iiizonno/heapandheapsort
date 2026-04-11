import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional
from managers.expense_manager import ExpenseManager


class TransactionFormWindow(tk.Toplevel):
    """
    Modal window for adding new transactions or editing existing ones.

    Provides a form interface for transaction data entry with validation
    and integration with the ExpenseManager for persistence.
    """

    def __init__(self, parent, manager: ExpenseManager, refresh_callback, transaction=None):
        """
        Initialize the transaction form window.

        Args:
            parent: Parent window for modal behavior
            manager: ExpenseManager instance for data operations
            refresh_callback: Function to call after successful save
            transaction: Existing Transaction to edit, or None for new transaction
        """
        super().__init__(parent)
        self.manager = manager
        self.refresh_callback = refresh_callback
        self.transaction = transaction

        title = "Edit Transaction" if transaction else "Add Transaction"
        self.title(title)
        self.geometry("500x380")
        self.resizable(False, False)

        self.create_form()

        if transaction:
            self.pre_fill()

    def create_form(self) -> None:
        """
        Create and arrange the transaction input form fields with elegant date picker.
        
        Builds an interactive form with date spinboxes, amount validation, category dropdown,
        and transaction type selection.
        """
        # Initialize date variables with current date
        current_date = datetime.now()
        self.year_var = tk.IntVar(value=current_date.year)
        self.month_var = tk.IntVar(value=current_date.month)
        self.day_var = tk.IntVar(value=current_date.day)

        row = 0
        # Date picker component with spinboxes for year/month/day
        tk.Label(self, text="Date:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=8, sticky="e")

        date_frame = tk.Frame(self)
        date_frame.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        # Year spinbox (2000-2030)
        tk.Label(date_frame, text="Year:").grid(row=0, column=0, padx=2)
        self.year_spin = tk.Spinbox(date_frame, from_=2000, to=2030, textvariable=self.year_var, width=6,
                                   command=self.update_day_range)
        self.year_spin.grid(row=0, column=1, padx=2)

        # Month spinbox (1-12)
        tk.Label(date_frame, text="Month:").grid(row=0, column=2, padx=2)
        self.month_spin = tk.Spinbox(date_frame, from_=1, to=12, textvariable=self.month_var, width=4,
                                    command=self.update_day_range)
        self.month_spin.grid(row=0, column=3, padx=2)

        # Day spinbox with dynamic range based on month/year
        tk.Label(date_frame, text="Day:").grid(row=0, column=4, padx=2)
        self.day_spin = tk.Spinbox(date_frame, from_=1, to=31, textvariable=self.day_var, width=4)
        self.day_spin.grid(row=0, column=5, padx=2)

        # Adjust day range for the current month/year
        self.update_day_range()
        row += 1

        # Amount input with real-time numeric validation
        tk.Label(self, text="Amount ($):", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.amount_entry = tk.Entry(self, width=25, validate="key", validatecommand=(self.register(self.validate_amount), "%P"))
        self.amount_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1

        # Category dropdown populated from ExpenseManager
        tk.Label(self, text="Category:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.category_combo = ttk.Combobox(self, values=[c.name for c in self.manager.categories], width=22, state='readonly')
        self.category_combo.grid(row=row, column=1, padx=10, pady=8)
        row += 1

        # Description text field
        tk.Label(self, text="Description:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.desc_entry = tk.Entry(self, width=25)
        self.desc_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1

        # Transaction type selection (Income or Expense)
        tk.Label(self, text="Type:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        type_frame = tk.Frame(self)
        type_frame.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        self.type_var = tk.StringVar(value="expense")
        tk.Radiobutton(type_frame, text="Expense", variable=self.type_var, value="expense").pack(side="left", padx=10)
        tk.Radiobutton(type_frame, text="Income", variable=self.type_var, value="income").pack(side="left", padx=10)

        # Submit button
        tk.Button(self, text="Save Transaction", command=self.save,
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                 relief="raised", bd=2, padx=20, pady=5).grid(
            row=row+1, column=0, columnspan=2, pady=25)

    def update_day_range(self) -> None:
        """
        Update the day spinbox range based on selected year and month.
        
        Prevents invalid dates (e.g., Feb 30) by dynamically adjusting the maximum
        day value and handling leap years correctly.
        """
        try:
            year = self.year_var.get()
            month = self.month_var.get()

            # Determine maximum days for the selected month
            if month in [1, 3, 5, 7, 8, 10, 12]:
                max_days = 31
            elif month in [4, 6, 9, 11]:
                max_days = 30
            elif month == 2:
                # Account for leap years
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    max_days = 29
                else:
                    max_days = 28
            else:
                max_days = 31

            # Update the day spinbox maximum
            self.day_spin.config(to=max_days)

            # Adjust current day if it exceeds the new maximum
            current_day = self.day_var.get()
            if current_day > max_days:
                self.day_var.set(max_days)

        except Exception:
            # Fallback: default to 31 if any error occurs
            self.day_spin.config(to=31)

    def validate_amount(self, value: str) -> bool:
        """
        Validate that the amount input is a valid positive number.
        
        This is used as a Tkinter validation command to prevent invalid user input.

        Args:
            value: The input string to validate

        Returns:
            True if valid (empty or positive number), False otherwise
        """
        if value == "":
            return True  # Allow empty field during editing

        try:
            amount = float(value)
            return amount >= 0  # Reject negative amounts
        except ValueError:
            return False  # Reject non-numeric input

    def get_selected_date(self) -> datetime:
        """
        Get the selected date from the spinboxes.
        
        Constructs a datetime object from the year, month, and day spinbox values.

        Returns:
            A datetime object representing the selected date at midnight

        Raises:
            ValueError: If the selected date combination is invalid
        """
        try:
            year = self.year_var.get()
            month = self.month_var.get()
            day = self.day_var.get()

            # Create and return datetime object
            selected_datetime = datetime(year, month, day)
            return selected_datetime
        except ValueError as e:
            raise ValueError(f"Invalid date selected: {e}")

    def pre_fill(self) -> None:
        """
        Populate form fields with existing transaction data for editing.
        
        Loads the current transaction values into all form fields to allow users
        to modify and save changes.
        """
        assert self.transaction is not None

        # Update date spinboxes from existing transaction
        self.year_var.set(self.transaction.date.year)
        self.month_var.set(self.transaction.date.month)
        self.day_var.set(self.transaction.date.day)

        # Populate other fields
        self.amount_entry.insert(0, str(self.transaction.amount))
        self.category_combo.set(self.transaction.category)
        self.desc_entry.insert(0, self.transaction.description)
        self.type_var.set(self.transaction.type)

    def save(self) -> None:
        """
        Validate form data and save the transaction to the manager.
        
        Performs comprehensive validation on all fields, displays user-friendly error
        messages for invalid input, and persists the transaction after saving.
        """
        try:
            # Construct and validate date
            date = self.get_selected_date()

            # Validate and parse amount
            amount_text = self.amount_entry.get().strip()
            if not amount_text:
                raise ValueError("Please enter an amount")
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")

            # Validate category selection
            category = self.category_combo.get().strip()
            if not category:
                raise ValueError("Please select a category")

            # Validate description
            desc = self.desc_entry.get().strip()
            if not desc:
                raise ValueError("Please enter a description")

            # Get transaction type
            trans_type = self.type_var.get()

            # Save the transaction
            if self.transaction:
                self.manager.edit_transaction(
                    self.transaction.id,
                    date=date,
                    amount=amount,
                    category=category,
                    description=desc,
                    trans_type=trans_type
                )
                messagebox.showinfo("Success", "Transaction updated successfully!")
            else:
                self.manager.add_transaction(date, amount, category, desc, trans_type)
                messagebox.showinfo("Success", "Transaction added successfully!")

            # Refresh parent window after saving
            self.master.after(100, self.refresh_callback)
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transaction: {str(e)}")

class AddTransactionWindow(TransactionFormWindow):
    """
    Legacy alias for TransactionFormWindow, maintained for backwards compatibility.
    
    Use TransactionFormWindow directly for new code.
    """
    def __init__(self, parent, manager, refresh_callback):
        super().__init__(parent, manager, refresh_callback)