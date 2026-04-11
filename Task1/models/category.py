class Category:
    """
    Represents a transaction category with an associated color for UI visualization.

    Categories help organize transactions and provide visual cues in charts and displays.
    Each category has a unique name and color code for consistent theming.
    """

    def __init__(self, name: str, color: str = "#000000"):
        """
        Initialize a new Category.

        Args:
            name: The category name (must be unique within the expense manager)
            color: Hex color code for UI visualization (defaults to black)
        """
        self.name = name
        self.color = color  # Hex code used for charts and visual categorization

    def __str__(self) -> str:
        """
        Return the category name as its string representation.

        Returns:
            The category name
        """
        return self.name
