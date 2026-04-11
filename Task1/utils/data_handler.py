import csv
import os
import logging
from models.transaction import Transaction

DATA_FILE = "data/transactions.csv"

# Configure module-level logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# CSV column requirements for valid transaction rows
REQUIRED_FIELDS = {"id", "date", "amount", "category", "description", "type"}


def load_transactions() -> list[Transaction]:
    """
    Load transactions from the CSV data file.

    Skips rows that are malformed or missing required fields, logging a
    warning for each skipped row so issues are visible without crashing.

    Returns:
        A list of Transaction objects (may be empty).
    """
    if not os.path.exists(DATA_FILE):
        logger.info("Data file '%s' not found — starting fresh.", DATA_FILE)
        return []

    transactions: list[Transaction] = []
    skipped = 0

    try:
        with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate that the header contains every required field
            if reader.fieldnames is None or not REQUIRED_FIELDS.issubset(reader.fieldnames):
                missing = REQUIRED_FIELDS - set(reader.fieldnames or [])
                logger.error(
                    "CSV header is missing required fields: %s — aborting load.",
                    missing,
                )
                return []

            for line_num, row in enumerate(reader, start=2):  # line 1 = header
                # Check that no required field is blank
                missing_in_row = [f for f in REQUIRED_FIELDS if not str(row.get(f, "")).strip()]
                if missing_in_row:
                    logger.warning(
                        "Row %d skipped — blank or missing field(s): %s",
                        line_num,
                        missing_in_row,
                    )
                    skipped += 1
                    continue

                try:
                    transactions.append(Transaction.from_dict(row))
                except (ValueError, KeyError, TypeError) as exc:
                    logger.warning(
                        "Row %d skipped — could not parse transaction: %s",
                        line_num,
                        exc,
                    )
                    skipped += 1

    except OSError as exc:
        logger.error("Failed to open '%s': %s", DATA_FILE, exc)
        return []

    if skipped:
        logger.warning(
            "Loaded %d transaction(s); skipped %d malformed row(s).",
            len(transactions),
            skipped,
        )
    else:
        logger.info("Loaded %d transaction(s) with no errors.", len(transactions))

    return transactions


def save_transactions(transactions: list[Transaction]) -> bool:
    """
    Persist a list of transactions to the CSV data file.

    Writes atomically by first writing to a temp file, then replacing the
    target so a mid-write crash never corrupts existing data.

    Args:
        transactions: The list of Transaction objects to save.

    Returns:
        True on success, False if an OS/IO error occurred.
    """
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    except OSError as exc:
        logger.error("Could not create data directory: %s", exc)
        return False

    tmp_path = DATA_FILE + ".tmp"

    try:
        with open(tmp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["id", "date", "amount", "category", "description", "type"],
                extrasaction="ignore",   # silently drop any extra keys from to_dict()
            )
            writer.writeheader()
            for trans in transactions:
                try:
                    writer.writerow(trans.to_dict())
                except (ValueError, AttributeError) as exc:
                    logger.warning("Skipping unserialisable transaction (id=%s): %s", getattr(trans, "id", "?"), exc)

        # Atomic replace — works on all platforms supported by Python 3.3+
        os.replace(tmp_path, DATA_FILE)
        logger.info("Saved %d transaction(s) to '%s'.", len(transactions), DATA_FILE)
        return True

    except OSError as exc:
        logger.error("Failed to save transactions: %s", exc)
        # Clean up the temp file if it was created
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False
