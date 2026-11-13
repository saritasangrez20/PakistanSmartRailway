"""Shared paths and constants for the PSR Information Assurance project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTERS = DATA / "registers"
FRAMEWORKS = DATA / "frameworks"
GROUND_TRUTH = DATA / "ground_truth"
ASSESSMENTS = DATA / "assessments"
OUTPUTS = ROOT / "outputs"

# Risk rating bands from A1 Section D.1.3
RATING_BANDS = [(16, 25, "Critical"), (10, 15, "High"), (5, 9, "Medium"), (1, 4, "Low")]

CONTROL_STATUSES = ("Implemented", "Partial", "Gap")
# Credit a control status earns when working out effectiveness or residual risk
STATUS_CREDIT = {"Implemented": 1.0, "Partial": 0.5, "Gap": 0.0}

# A2 Section D.4 compliance weights
COMPLIANCE_WEIGHTS = {"Compliant": 1.0, "Partially compliant": 0.5, "Weak": 0.25, "Non-compliant": 0.0}

READINESS_CREDIT = {"Y": 1.0, "P": 0.5, "N": 0.0}

# Overall IA status bands applied to governance maturity (out of 5)
MATURITY_BANDS = [(4.5, "OPTIMIZED"), (3.5, "MANAGED"), (2.5, "DEFINED"), (1.5, "DEVELOPING"), (0.0, "INITIAL")]


def rating_for(score: float) -> str:
    for low, high, name in RATING_BANDS:
        if low <= score <= high:
            return name
    raise ValueError(f"score {score} is outside 1 to 25")


def split_ids(value) -> list[str]:
    """Split a semicolon separated ID cell into a clean list."""
    if value is None or (isinstance(value, float) and value != value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]
