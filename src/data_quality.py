"""
Data-quality checks for the accessibility/CSR dataset: exactly the kind
of validation a real quarterly CSR-impact tracker needs before any KPI
gets reported to leadership.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.data_sources import AccessibilityRecord


@dataclass
class DataQualityFlag:
    department: str
    quarter: str
    issue_type: str
    detail: str


def find_accommodation_overcounts(records: list[AccessibilityRecord]) -> list[DataQualityFlag]:
    """Flag any record where completed accommodations exceed requested
    accommodations in the same quarter -- logically impossible, and a
    real, recurring data-entry error pattern (completions from a prior
    quarter miscounted into the current one)."""
    flags = []
    for r in records:
        if r.workplace_accommodations_completed > r.workplace_accommodations_requested:
            flags.append(DataQualityFlag(
                department=r.department, quarter=r.quarter,
                issue_type="accommodation_overcount",
                detail=(
                    f"{r.workplace_accommodations_completed} completed exceeds "
                    f"{r.workplace_accommodations_requested} requested"
                ),
            ))
    return flags


def find_missing_training_metrics(records: list[AccessibilityRecord]) -> list[DataQualityFlag]:
    """Flag records with a missing (NaN) training-completion percentage
    -- a metric not yet reported, not silently treated as 0%."""
    flags = []
    for r in records:
        if math.isnan(r.accessibility_training_completion_pct):
            flags.append(DataQualityFlag(
                department=r.department, quarter=r.quarter,
                issue_type="missing_training_metric",
                detail="accessibility_training_completion_pct not reported",
            ))
    return flags


def run_all_checks(records: list[AccessibilityRecord]) -> list[DataQualityFlag]:
    return find_accommodation_overcounts(records) + find_missing_training_metrics(records)
