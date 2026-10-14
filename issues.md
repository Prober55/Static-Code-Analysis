# Static Code Analysis — Issues and Fixes

## Overview
This document records the issues identified in `scholarship_disbursement.py` by static code analysis tools (**Bandit**, **Pylint**, and **Flake8**), along with their classifications, descriptions, and the remediation approaches applied.

---

## Issue Summary Table

| Issue | Tool / Code | Type | Line(s) (Original) | Description | Fix Approach |
|---|---|---|---|---|---|
| **SQL Query String Formatting** | Bandit `B608` | Security (Medium) | 10 | User-provided values (`student`, `scheme`, `amount`) are inserted directly into an SQL query string via `%` formatting, creating a critical SQL injection vector (CWE-89). | Replaced string interpolation with parameterized SQL query placeholders (`?`) passed as a tuple. |
| **Mutable Default Argument** | Pylint `W0102` | Bug / Correctness | 9 | The default argument `audit=[]` creates a mutable default list that is shared across all function calls, accumulating state unintentionally. | Changed default value to `None` and initialized a fresh list inside `grant()` (`if audit is None: audit = []`). |
| **Shell Command Execution** | Bandit `B605`, `B607` | Security / Quality | 26 | `os.system("echo archiving awards")` invokes a system shell with a partial executable path, introducing potential command injection risks (CWE-78) and unnecessary process overhead. | Replaced shell invocation with native Python `print("archiving awards")` and removed the unused `os` import. |
| **Broad Exception Handling & Silent Pass** | Bandit `B110`, Pylint `W0718` | Quality / Robustness | 27–28 | Catching overly broad `Exception` followed by `pass` silently suppresses failures and bugs (CWE-703), masking runtime errors. | Removed the unnecessary try-except block and exception swallowing. |
| **Incorrect `None` Comparison** | Flake8 `E711`, Pylint `C0121` | Style / PEP 8 | 32 | Used equality operator `scheme == None` instead of identity comparison (`is None`). | Changed condition to `if scheme is None:`. |
| **Non-Compliant Function Naming** | Pylint `C0103` | Style / PEP 8 | 31 | Function name `bySchemeCount` used camelCase instead of PEP 8 snake_case style convention. | Renamed to `by_scheme_count` (with backward compatibility alias provided). |
| **Repeated Award Disbursement** | Logic / Defect | Correctness | 17–20 | Calling `disburse(award_id)` multiple times on the same award repeatedly increments `disbursed_total` even if the award was already disbursed. | Updated SQL query to filter `WHERE id = ? AND disbursed = 0` so only undisbursed awards are processed, and ensured consistent return values. |
| **Global State Mutation & Naming** | Pylint `W0603`, `C0103` | Maintainability / Quality | 6, 16 | Module-level global variable `disbursed_total` mutated via `global` keyword impairs modularity, testability, and PEP 8 constant naming. | Replaced global variable mutation with direct SQL database aggregation query (`SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1`), backed by `get_disbursed_total()` and `__getattr__` for backward compatibility. |
| **Missing Docstrings** | Pylint `C0114`, `C0116` | Documentation | 1, 9, 15, 24, 31, 37 | Module and functions lacked descriptive docstrings explaining their purpose and arguments. | Added descriptive PEP 257 docstrings to the module and all functions. |
| **Line Length Limit Exceeded** | Flake8 `E501`, Pylint `C0301` | Style / PEP 8 | 5, 10, 17, 19, 34 | Several lines exceeded the standard PEP 8 79-character limit (reaching up to 130 characters). | Reformatted multi-line SQL queries and function parameters to stay strictly within 79 characters. |

---

## Verification Results

After applying the fixes, all three static analysis tools were executed against the cleaned `scholarship_disbursement.py`:

- **Pylint**: **10.00 / 10.00** (0 warnings, 0 conventions, 0 refactoring flags)
- **Bandit**: **No issues identified** (0 High, 0 Medium, 0 Low)
- **Flake8**: **0 errors** (full PEP 8 compliance)
- **Runtime verification**: `python scholarship_disbursement.py` produces the expected output:
  ```text
  50000 None
  1 50000
  archiving awards
  ```
