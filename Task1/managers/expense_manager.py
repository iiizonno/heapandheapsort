from datetime import datetime
from typing import Dict, List, Optional, Union
from models.transaction import Transaction
from models.category import Category
from models.budget import Budget


class ExpenseManager:
    """
    Central business logic manager for the expense tracking application.

    This class handles all transaction operations, category management, budgeting,
    and provides methods for filtering, summarizing, and analyzing financial data.
    It serves as the main interface between the GUI and data persistence layers.
    """

    def __init__(self):
        """
        Initialize the ExpenseManager with default categories and empty transaction list.
        
        Sets up predefined expense categories for UI organization, initializes a budget
        tracker, and prepares for transaction management.
        """
        self.transactions: List[Transaction] = []
        # Predefined categories with associated UI colors
        self.categories: List[Category] = [
            Category("Food", "#FF6347"),              # Tomato red
            Category("Transport", "#4682B4"),         # Steel blue
            Category("Rent", "#8B4513"),              # Saddle brown
            Category("Entertainment", "#FFD700"),     # Gold
            Category("Salary", "#32CD32"),            # Lime green
            Category("Utilities", "#1E90FF"),         # Dodger blue
            Category("Shopping", "#FF69B4"),          # Hot pink
            Category("Groceries", "#32CD99"),         # Mint green
            Category("Bonus", "#FFA500"),             # Orange
        ]
        self.budget = Budget()  # Budget manager for expense limits
        self.next_id = 1        # Counter for assigning unique transaction IDs

    def add_transaction(self, date: datetime, amount: float, category: str,
                        description: str = "", trans_type: str = "expense") -> Transaction:
        """
        Create and add a new transaction to the manager.

        Args:
            date: The date of the transaction
            amount: The monetary amount (must be non-negative)
            category: The category name (must exist in self.categories)
            description: Optional description of the transaction
            trans_type: Either "income" or "expense" (defaults to "expense")

        Returns:
            The newly created Transaction object

        Raises:
            ValueError: If category doesn't exist or amount is negative
        """
        if category not in [c.name for c in self.categories]:
            raise ValueError(f"Category '{category}' does not exist.")
        transaction_id = self.next_id
        new_transaction = Transaction(
            trans_id=transaction_id,
            date=date,
            amount=amount,
            category=category,
            description=description,
            trans_type=trans_type,
        )
        self.transactions.append(new_transaction)
        self.next_id += 1
        return new_transaction

    def edit_transaction(self, trans_id: int, **updates) -> bool:
        """
        Update an existing transaction with the provided field changes.
        
        Validates all fields before applying updates to ensure data consistency.

        Args:
            trans_id: The ID of the transaction to update
            **updates: Keyword arguments for fields to update (date, amount, category, description, trans_type)

        Returns:
            True if the transaction was found and updated, False otherwise

        Raises:
            ValueError: If category doesn't exist, amount is negative, or type is invalid
        """
        match = next((trans for trans in self.transactions if trans.id == trans_id), None)
        if match is None:
            return False

        # Validate category if being updated
        if "category" in updates:
            category = updates["category"]
            if category not in [c.name for c in self.categories]:
                raise ValueError(f"Category '{category}' does not exist.")

        # Validate and convert amount if being updated
        if "amount" in updates:
            amount = float(updates["amount"])
            if amount < 0:
                raise ValueError("Amount cannot be negative.")
            updates["amount"] = amount

        # Handle transaction type conversion (from trans_type to type)
        if "trans_type" in updates:
            trans_type = updates.pop("trans_type")
            if trans_type not in ["income", "expense"]:
                raise ValueError("Type must be 'income' or 'expense'.")
            updates["type"] = trans_type

        # Apply validated updates to the transaction object
        transaction_updated = False
        for key, value in updates.items():
            if hasattr(match, key):
                setattr(match, key, value)
                transaction_updated = True
        return transaction_updated

    def delete_transaction(self, trans_id: int) -> bool:
        """
        Remove a transaction from the manager by its ID.

        Args:
            trans_id: The ID of the transaction to delete

        Returns:
            True if the transaction was found and deleted, False otherwise
        """
        match = next((trans for trans in self.transactions if trans.id == trans_id), None)
        if match is None:
            return False
        self.transactions.remove(match)
        return True

    def get_transactions(self, filter_year: Optional[str] = None,
                         filter_month: Optional[str] = None,
                         filter_category: Optional[str] = None,
                         search_keyword: Optional[str] = None) -> List[Transaction]:
        """
        Retrieve transactions with optional filtering.

        Args:
            filter_year: Year to filter by (as string), or None/"All" for no year filter
            filter_month: Month to filter by (as string "01"-"12"), or None/"All" for no month filter
            filter_category: Category name to filter by, or None for no category filter
            search_keyword: Keyword to search in descriptions, or None for no search filter

        Returns:
            List of Transaction objects matching all applied filters
        """
        results = list(self.transactions)

        # Filter by year if specified
        if filter_year and filter_year != "All":
            try:
                year_int = int(filter_year)
            except ValueError:
                year_int = None
            if year_int is not None:
                results = [
                    trans for trans in results
                    if trans.date.year == year_int
                ]

        # Filter by month if specified
        if filter_month and filter_month != "All":
            month_str = filter_month.zfill(2)
            results = [
                trans for trans in results
                if trans.date.strftime("%m") == month_str
            ]

        # Filter by category if specified
        if filter_category:
            results = [
                trans for trans in results
                if trans.category == filter_category
            ]

        # Filter by search keyword in description if specified
        if search_keyword:
            keyword = search_keyword.strip().lower()
            results = [
                trans for trans in results
                if keyword in trans.description.lower()
            ]

        return results

    def get_monthly_summary(self, year: Optional[str] = None, month: Optional[str] = None) -> Dict:
        """
        Calculate financial summary for the specified time period.

        Args:
            year: Year to summarize (as string), or None/"All" for all years
            month: Month to summarize (as string "01"-"12"), or None/"All" for all months

        Returns:
            Dictionary containing:
            - total_income: Sum of all income transactions
            - total_expense: Sum of all expense transactions
            - net: Income minus expenses
            - per_category: Dict of category -> total expense amount
        """
        year = year or "All"
        month = month or "All"

        # Get transactions for the specified period
        if year != "All" and month == "All":
            transactions = self.get_transactions(filter_year=year)
        elif year == "All" and month != "All":
            transactions = self.get_transactions(filter_month=month)
        elif year != "All" and month != "All":
            transactions = self.get_transactions(filter_year=year, filter_month=month)
        else:
            transactions = list(self.transactions)

        # Calculate totals
        total_income = 0.0
        total_expense = 0.0
        per_category: Dict[str, float] = {}

        for trans in transactions:
            if trans.type == "income":
                total_income += trans.amount
            else:
                total_expense += trans.amount
                per_category[trans.category] = per_category.get(trans.category, 0.0) + trans.amount

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net": total_income - total_expense,
            "per_category": per_category,
        }

    def get_remaining_budget(self, category: str, year: Optional[str] = None, month: Optional[str] = None) -> float:
        """
        Calculate remaining budget for a specific category in the given period.

        Args:
            category: The category name to check
            year: Year to check (as string), or None for current/all years
            month: Month to check (as string "01"-"12"), or None for current/all months

        Returns:
            Remaining budget amount (limit - spent). Positive means under budget.
        """
        category_limit = self.budget.get_limit(category)
        transactions = self.get_transactions(
            filter_year=year,
            filter_month=month
        )
        spent = sum(
            trans.amount for trans in transactions
            if trans.category == category and trans.type == "expense"
        )
        return category_limit - spent

    def get_total_remaining_budget(self, year: Optional[str] = None, month: Optional[str] = None) -> float:
        """
        Calculate total remaining budget across all categories for the given period.

        If a total budget limit is set, uses that. Otherwise sums up individual category budgets.

        Args:
            year: Year to check (as string), or None for current/all years
            month: Month to check (as string "01"-"12"), or None for current/all months

        Returns:
            Total remaining budget amount
        """
        summary = self.get_monthly_summary(year, month)

        if self.budget.total_limit > 0:
            return self.budget.total_limit - summary["total_expense"]

        return sum(
            max(self.get_remaining_budget(category, year, month), 0.0)
            for category in self.budget.monthly_limits
        )

    def get_alerts(self, year: Optional[str] = None, month: Optional[str] = None) -> List[str]:
        """
        Generate budget alert messages for categories that have exceeded their limits.

        Args:
            year: Year to check (as string), or None for current/all years
            month: Month to check (as string "01"-"12"), or None for current/all months

        Returns:
            List of alert message strings for budget overruns
        """
        summary = self.get_monthly_summary(year, month)
        alerts: List[str] = []

        # Check individual category limits
        for category, limit in self.budget.monthly_limits.items():
            spent = sum(
                trans.amount for trans in self.get_transactions(filter_year=year, filter_month=month)
                if trans.category == category and trans.type == "expense"
            )
            if spent > limit:
                alerts.append(
                    f"Budget exceeded for {category}: spent ${spent:,.2f}, limit ${limit:,.2f}."
                )

        # Check total budget limit
        if self.budget.total_limit > 0 and summary["total_expense"] > self.budget.total_limit:
            alerts.append(
                f"Total expense exceeded: spent ${summary['total_expense']:,.2f}, total limit ${self.budget.total_limit:,.2f}."
            )

        return alerts

    def get_pie_chart_data(self, trans_type: str = "expense", year: Optional[str] = None, month: Optional[str] = None) -> Dict:
        """
        Generate data for pie chart visualization of income or expense by category.

        Args:
            trans_type: "income" or "expense" to choose the transaction type
            year: Year to include (as string), or None for all years
            month: Month to include (as string "01"-"12"), or None for all months

        Returns:
            Dictionary with 'labels', 'sizes', and 'colors' lists for pie chart rendering
        """
        if trans_type not in {"income", "expense"}:
            raise ValueError("trans_type must be 'income' or 'expense'")

        transactions = self.get_transactions(
            filter_year=year,
            filter_month=month,
            filter_category=None,
            search_keyword=None
        )
        per_category: Dict[str, float] = {}

        for trans in transactions:
            if trans.type == trans_type:
                per_category[trans.category] = per_category.get(trans.category, 0.0) + trans.amount

        labels = []
        sizes = []
        colors = []

        for category in self.categories:
            amount = per_category.get(category.name, 0.0)
            if amount <= 0:
                continue
            labels.append(category.name)
            sizes.append(amount)
            colors.append(category.color)

        return {
            "labels": labels,
            "sizes": sizes,
            "colors": colors,
        }

    def get_expense_by_category(self, year: Optional[str] = None, month: Optional[str] = None) -> List[Dict[str, Union[str, float]]]:
        """
        Return expense totals by category for the selected period.

        Args:
            year: Year to include (as string), or None for all years
            month: Month to include (as string "01"-"12"), or None for all months

        Returns:
            List of dictionaries containing category name, expense amount, and chart color.
        """
        summary = self.get_monthly_summary(year, month)
        chart_data: List[Dict[str, Union[str, float]]] = []

        for category in self.categories:
            amount = summary["per_category"].get(category.name, 0.0)
            if amount > 0:
                chart_data.append({
                    "name": category.name,
                    "amount": amount,
                    "color": category.color,
                })

        return chart_data
