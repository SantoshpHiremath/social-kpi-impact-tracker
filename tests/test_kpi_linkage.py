import math

from src.data_sources import AccessibilityRecord, DepartmentPerformanceRecord
from src.kpi_linkage import (
    compute_accessibility_kpis, link_to_department_performance, program_progress_trend,
)


def make_access_record(**overrides):
    defaults = dict(
        department="Engineering Strategy", quarter="2025-Q1", headcount=100,
        employees_with_disability=8, workplace_accommodations_completed=3,
        workplace_accommodations_requested=4, accessibility_training_completion_pct=80.0,
        source="HR Quarterly Report",
    )
    defaults.update(overrides)
    return AccessibilityRecord(**defaults)


def make_perf_record(**overrides):
    defaults = dict(
        department="Engineering Strategy", quarter="2025-Q1",
        on_time_delivery_pct=91.5, employee_engagement_score=4.1,
        voluntary_attrition_pct=5.0, source="Departmental Performance Dashboard",
    )
    defaults.update(overrides)
    return DepartmentPerformanceRecord(**defaults)


def test_representation_pct_computed_correctly():
    r = make_access_record(headcount=200, employees_with_disability=16)
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.disability_representation_pct == 8.0


def test_fulfillment_pct_computed_correctly():
    r = make_access_record(workplace_accommodations_completed=3, workplace_accommodations_requested=4)
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.accommodation_fulfillment_pct == 75.0


def test_fulfillment_pct_none_on_overcount():
    r = make_access_record(workplace_accommodations_completed=5, workplace_accommodations_requested=3)
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.accommodation_fulfillment_pct is None


def test_fulfillment_pct_none_on_zero_requested():
    r = make_access_record(workplace_accommodations_completed=0, workplace_accommodations_requested=0)
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.accommodation_fulfillment_pct is None


def test_training_pct_none_on_missing():
    r = make_access_record(accessibility_training_completion_pct=float("nan"))
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.training_completion_pct is None


def test_zero_headcount_does_not_divide_by_zero():
    r = make_access_record(headcount=0, employees_with_disability=0)
    kpi = compute_accessibility_kpis([r])[0]
    assert kpi.disability_representation_pct == 0.0


def test_link_joins_by_department_and_quarter():
    access = make_access_record(department="Procurement", quarter="2025-Q2")
    perf = make_perf_record(department="Procurement", quarter="2025-Q2", on_time_delivery_pct=88.0)
    kpi = compute_accessibility_kpis([access])
    linked = link_to_department_performance(kpi, [perf])
    assert len(linked) == 1
    assert linked[0].department == "Procurement"
    assert linked[0].on_time_delivery_pct == 88.0


def test_link_skips_unmatched_quarter_rather_than_fabricating():
    access = make_access_record(department="Procurement", quarter="2025-Q2")
    perf = make_perf_record(department="Procurement", quarter="2025-Q3")  # different quarter
    kpi = compute_accessibility_kpis([access])
    linked = link_to_department_performance(kpi, [perf])
    assert linked == []


def test_link_skips_unmatched_department():
    access = make_access_record(department="Procurement", quarter="2025-Q2")
    perf = make_perf_record(department="Production", quarter="2025-Q2")
    kpi = compute_accessibility_kpis([access])
    linked = link_to_department_performance(kpi, [perf])
    assert linked == []


def test_progress_trend_sorted_by_quarter():
    records = [
        make_access_record(department="X", quarter="2025-Q3", accessibility_training_completion_pct=60.0),
        make_access_record(department="X", quarter="2025-Q1", accessibility_training_completion_pct=40.0),
        make_access_record(department="X", quarter="2025-Q2", accessibility_training_completion_pct=50.0),
    ]
    kpis = compute_accessibility_kpis(records)
    trend = program_progress_trend(kpis, "X")
    quarters = [q for q, _ in trend]
    assert quarters == ["2025-Q1", "2025-Q2", "2025-Q3"]


def test_progress_trend_filters_by_department():
    records = [
        make_access_record(department="X", quarter="2025-Q1"),
        make_access_record(department="Y", quarter="2025-Q1"),
    ]
    kpis = compute_accessibility_kpis(records)
    trend = program_progress_trend(kpis, "X")
    assert len(trend) == 1
