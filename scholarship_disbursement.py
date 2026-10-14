"""Module for managing scholarship awards, disbursements, and ledgers."""

import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE awards ("
    "id INTEGER PRIMARY KEY, "
    "student TEXT, "
    "scheme TEXT, "
    "amount INTEGER, "
    "disbursed INTEGER)"
)


def grant(student, scheme, amount, audit=None):
    """Grant a scholarship award to a student under a specified scheme."""
    if audit is None:
        audit = []
    conn.execute(
        "INSERT INTO awards (student, scheme, amount, disbursed) "
        "VALUES (?, ?, ?, 0)",
        (student, scheme, amount),
    )
    audit.append(student)
    return audit


def disburse(award_id):
    """Disburse an award by ID if not already disbursed."""
    row = conn.execute(
        "SELECT amount FROM awards WHERE id = ? AND disbursed = 0",
        (award_id,),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE awards SET disbursed = 1 WHERE id = ?",
            (award_id,),
        )
        return row[0]
    return None


def get_disbursed_total():
    """Calculate and return the total amount of all disbursed awards."""
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
    ).fetchone()
    return row[0]


def archive():
    """Archive awards records."""
    print("archiving awards")


def by_scheme_count(scheme):
    """Return the number of awards under the given scheme."""
    if scheme is None:
        return 0
    row = conn.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?",
        (scheme,),
    ).fetchone()
    return row[0]


# Backwards compatibility alias for camelCase naming
bySchemeCount = by_scheme_count


def __getattr__(name):
    """Module-level attribute fallback for backward compatibility."""
    if name == "disbursed_total":
        return get_disbursed_total()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main():
    """Execute scholarship disbursement workflow."""
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), get_disbursed_total())
    archive()


if __name__ == "__main__":
    main()
