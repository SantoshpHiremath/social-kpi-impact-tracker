"""
Links accessibility/CSR-program KPIs to departmental performance
metrics, linking social KPIs to overall departmental performance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.data_sources import AccessibilityRecord, DepartmentPerformanceRecord


@dataclass
class AccessibilityProgressKPI:
    department: str
    quarter: str
    disability_representation_pct: float  # employees_with_disability / headcount
    accommodation_fulfillment_pct: float  # completed / requested (None if overcount flagged)
    training_completion_pct: float | None


@dataclass
class LinkedDepartmentSummary:
    department: str
    quarter: str
    disability_representation_pct: float
    accommodation_fulfillment_pct: float
    training_completion_pct: float | None
    on_time_delivery_pct: float
    employee_engagement_score: float
    voluntary_attrition_pct: float


def compute_accessibility_kpis(records: list[AccessibilityRecord]) -> list[AccessibilityProgressKPI]:
    """Compute the accessibility-program progress KPIs, excluding
    overcount rows from the fulfillment-rate calculation (a rate above
    100% is not a meaningful KPI value, not something to report as-is)."""
    kpis = []
    for r in records:
        representation = round((r.employees_with_disability / r.headcount) * 100, 2) if r.headcount else 0.0
        if r.workplace_accommodations_completed > r.workplace_accommodations_requested:
            fulfillment = None  # data-quality issue -- don't report a >100% rate
        elif r.workplace_accommodations_requested == 0:
            fulfillment = None
        else:
            fulfillment = round(
                (r.workplace_accommodations_completed / r.workplace_accommodations_requested) * 100, 2
            )
        training = (
            None if math.isnan(r.accessibility_training_completion_pct)
            else r.accessibility_training_completion_pct
        )
        kpis.append(AccessibilityProgressKPI(
            department=r.department, quarter=r.quarter,
            disability_representation_pct=representation,
            accommodation_fulfillment_pct=fulfillment,
            training_completion_pct=training,
        ))
    return kpis


def link_to_department_performance(
    accessibility_kpis: list[AccessibilityProgressKPI],
    performance_records: list[DepartmentPerformanceRecord],
) -> list[LinkedDepartmentSummary]:
    """Joins accessibility-program KPIs to departmental performance by
    (department, quarter) -- an explicit join, not a positional zip, so
    mismatched or missing quarters don't silently produce wrong pairs."""
    perf_index = {(p.department, p.quarter): p for p in performance_records}
    linked = []
    for kpi in accessibility_kpis:
        key = (kpi.department, kpi.quarter)
        perf = perf_index.get(key)
        if perf is None:
            continue  # no matching performance record for this dept/quarter -- skip, don't fabricate
        linked.append(LinkedDepartmentSummary(
            department=kpi.department, quarter=kpi.quarter,
            disability_representation_pct=kpi.disability_representation_pct,
            accommodation_fulfillment_pct=kpi.accommodation_fulfillment_pct,
            training_completion_pct=kpi.training_completion_pct,
            on_time_delivery_pct=perf.on_time_delivery_pct,
            employee_engagement_score=perf.employee_engagement_score,
            voluntary_attrition_pct=perf.voluntary_attrition_pct,
        ))
    return linked


def program_progress_trend(kpis: list[AccessibilityProgressKPI], department: str) -> list[tuple[str, float | None]]:
    """Returns (quarter, training_completion_pct) pairs for one
    department in quarter order -- the trend view a leadership report
    actually needs, not just a snapshot."""
    dept_kpis = [k for k in kpis if k.department == department]
    dept_kpis.sort(key=lambda k: k.quarter)
    return [(k.quarter, k.training_completion_pct) for k in dept_kpis]
