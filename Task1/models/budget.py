from typing import Dict


class Budget:
    """
    Manages budget limits for expense tracking.

    Supports both individual category limits and a total monthly spending limit.
    Budgets help users track spending against predefined financial goals.
    """

    def __init__(self):
        """
        Initialize an empty budget with no limits set.
        """
        self.monthly_limits: Dict[str, float] = {}  # Maps category name to limit amount
        self.total_limit: float = 0.0               # Overall monthly spending limit

    def set_limit(self, category: str, amount: float) -> None:
        """
        Set a monthly spending limit for a specific category.

        Args:
            category: The category name to set the limit for
            amount: The monthly spending limit amount
        """
        self.monthly_limits[category] = amount

    def set_total_limit(self, amount: float) -> None:
        """
        Set a total monthly spending limit across all categories.

        Args:
            amount: The total monthly spending limit
        """
        self.total_limit = amount

    def get_limit(self, category: str) -> float:
        """
        Get the monthly spending limit for a specific category.

        Args:
            category: The category name to get the limit for

        Returns:
            The spending limit for the category, or 0.0 if no limit is set
        """
        return self.monthly_limits.get(category, 0.0)