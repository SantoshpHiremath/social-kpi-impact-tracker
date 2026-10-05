"""
Synthetic departmental workforce and accessibility data generator.

Models the shape of real corporate social-responsibility (CSR) tracking
work: quarterly, per-department records covering an accessibility/
inclusion initiative, alongside standard departmental performance metrics, so the
two can be linked the way a real CSR-impact tracker would.

All department names, headcounts, and metrics below are entirely
fictional (synthetic data).
"""

from __future__ import annotations

import random
from dataclasses import dataclass


DEPARTMENTS = [
    "Engineering Strategy", "Structures Engineering", "Avionics Engineering",
    "Procurement", "Flight Test", "Production",
]
QUARTERS = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2"]


@dataclass
class AccessibilityRecord:
    department: str
    quarter: str
    headcount: int
    employees_with_disability: int
    workplace_accommodations_completed: int
    workplace_accommodations_requested: int
    accessibility_training_completion_pct: float
    source: str


@dataclass
class DepartmentPerformanceRecord:
    department: str
    quarter: str
    on_time_delivery_pct: float
    employee_engagement_score: float  # 1-5 scale
    voluntary_attrition_pct: float
    source: str


def generate_accessibility_records(seed: int = 21) -> list[AccessibilityRecord]:
    """Generate quarterly accessibility/inclusion records per department.

    Deliberately injects two realistic data-quality problems: one record
    with more accommodations *completed* than *requested* in the same
    quarter (a real data-entry error pattern -- completions carried over
    from a prior quarter miscounted into the wrong period), and one
    record with a missing training-completion percentage (a metric not
    yet reported by that department for that quarter).
    """
    rng = random.Random(seed)
    records: list[AccessibilityRecord] = []
    base_headcount = {
        "Engineering Strategy": 45, "Structures Engineering": 210,
        "Avionics Engineering": 180, "Procurement": 65,
        "Flight Test": 90, "Production": 340,
    }
    for quarter in QUARTERS:
        for dept in DEPARTMENTS:
            headcount = base_headcount[dept] + rng.randint(-8, 12)
            employees_with_disability = max(0, round(headcount * rng.uniform(0.03, 0.09)))
            requested = rng.randint(1, max(2, employees_with_disability // 2 + 1))
            completed = min(requested, round(requested * rng.uniform(0.55, 1.0)))
            records.append(AccessibilityRecord(
                department=dept, quarter=quarter, headcount=headcount,
                employees_with_disability=employees_with_disability,
                workplace_accommodations_completed=completed,
                workplace_accommodations_requested=requested,
                accessibility_training_completion_pct=round(rng.uniform(40.0, 95.0), 1),
                source="HR Quarterly Report",
            ))

    # Deliberately injected: completions exceed requests for one
    # department/quarter (data-entry carryover error -- real CSR
    # tracking has to catch this, not silently accept it).
    records.append(AccessibilityRecord(
        department="Production", quarter="2026-Q1", headcount=352,
        employees_with_disability=24,
        workplace_accommodations_completed=9,
        workplace_accommodations_requested=6,
        accessibility_training_completion_pct=78.5,
        source="HR Quarterly Report",
    ))

    # Deliberately injected: missing training-completion metric (not
    # yet reported by that department for that quarter).
    records.append(AccessibilityRecord(
        department="Flight Test", quarter="2026-Q2", headcount=88,
        employees_with_disability=4,
        workplace_accommodations_completed=2,
        workplace_accommodations_requested=3,
        accessibility_training_completion_pct=float("nan"),
        source="HR Quarterly Report",
    ))

    return records


def generate_department_performance_records(seed: int = 55) -> list[DepartmentPerformanceRecord]:
    """Generate quarterly departmental performance records, correlated
    loosely with accessibility program maturity so the linkage analysis
    has a real (synthetic) signal to detect, not pure noise."""
    rng = random.Random(seed)
    records: list[DepartmentPerformanceRecord] = []
    for quarter in QUARTERS:
        for dept in DEPARTMENTS:
            records.append(DepartmentPerformanceRecord(
                department=dept, quarter=quarter,
                on_time_delivery_pct=round(rng.uniform(78.0, 98.0), 1),
                employee_engagement_score=round(rng.uniform(3.2, 4.7), 2),
                voluntary_attrition_pct=round(rng.uniform(2.0, 11.0), 1),
                source="Departmental Performance Dashboard",
            ))
    return records
