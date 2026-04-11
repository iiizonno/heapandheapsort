"""
main.py — Entry point for the Expense Tracker application.

Responsibilities (Member C):
  - Bootstrap ExpenseManager and restore persisted state.
  - Launch the Tkinter GUI via MainWindow.
  - Save all transactions back to disk when the window is closed.
"""

import sys
import logging

from managers.expense_manager import ExpenseManager
from gui.main_window import MainWindow
from utils.data_handler import load_transactions, save_transactions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def bootstrap_manager() -> ExpenseManager:
    """
    Create an ExpenseManager and populate it from the saved CSV (if any).

    Returns:
        A fully initialised ExpenseManager ready for use.
    """
    manager = ExpenseManager()

    loaded = load_transactions()
    if loaded:
        manager.transactions = loaded
        # Set next_id to one beyond the highest existing id so new
        # transactions never collide with loaded ones.
        manager.next_id = max(t.id for t in loaded) + 1
        logger.info(
            "Restored %d transaction(s); next ID will be %d.",
            len(loaded),
            manager.next_id,
        )
    else:
        manager.next_id = 1
        logger.info("No existing data found — starting with an empty ledger.")

    return manager


def main() -> None:
    manager = bootstrap_manager()
    window = MainWindow(manager)

    def on_close() -> None:
        """Persist data then destroy the window."""
        ok = save_transactions(manager.transactions)
        if not ok:
            # Warn the user that data could not be saved before quitting.
            try:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Save Failed",
                    "Your transactions could not be saved to disk.\n"
                    "Check the console for details.",
                )
            except Exception:
                logger.error("Transactions could NOT be saved — see above for details.")
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    try:
        window.mainloop()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — saving and exiting.")
        save_transactions(manager.transactions)
        sys.exit(0)


if __name__ == "__main__":
    main()
