from datetime import datetime


class Transaction:
    """
    Represents a single financial transaction in the expense tracking system.

    A transaction can be either income (money received) or expense (money spent).
    Each transaction has a unique ID, date, amount, category, and optional description.
    """

    def __init__(self, trans_id: int, date: datetime, amount: float, category: str,
                 description: str = "", trans_type: str = "expense"):
        """
        Initialize a new Transaction.

        Args:
            trans_id: Unique identifier for this transaction
            date: Date when the transaction occurred
            amount: Monetary amount (must be non-negative)
            category: Category this transaction belongs to
            description: Optional description of the transaction
            trans_type: Either "income" or "expense" (defaults to "expense")

        Raises:
            ValueError: If amount is negative or type is not "income"/"expense"
        """
        self.id = trans_id
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description
        self.type = trans_type  # "income" or "expense"

        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.type not in ["income", "expense"]:
            raise ValueError("Type must be 'income' or 'expense'")

    def to_dict(self) -> dict:
        """
        Convert the transaction to a dictionary for serialization.

        Returns:
            Dictionary representation suitable for CSV storage
        """
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """
        Create a Transaction instance from a dictionary.

        Args:
            data: Dictionary containing transaction data (typically from CSV)

        Returns:
            New Transaction instance
        """
        return cls(
            trans_id=int(data["id"]),
            date=datetime.strptime(data["date"], "%Y-%m-%d"),
            amount=float(data["amount"]),
            category=data["category"],
            description=data["description"],
            trans_type=data["type"]
        )

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the transaction.

        Returns:
            Formatted string showing date, type, category, amount, and description
        """
        return f"{self.date.strftime('%Y-%m-%d')} | {self.type.upper()} | {self.category} | ${self.amount:.2f} | {self.description}"
