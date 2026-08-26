import math

from src.data_sources import (
    generate_accessibility_records, generate_department_performance_records,
    DEPARTMENTS, QUARTERS,
)


def test_reproducible_with_same_seed():
    # NaN != NaN in Python, so dataclass equality can't be used directly
    # when a field may be NaN (the deliberately-injected missing-metric
    # row). Compare field-by-field with a NaN-aware check instead.
    a = generate_accessibility_records(seed=21)
    b = generate_accessibility_records(seed=21)
    assert len(a) == len(b)
    for ra, rb in zip(a, b):
        assert ra.department == rb.department
        assert ra.quarter == rb.quarter
        assert ra.headcount == rb.headcount
        assert ra.employees_with_disability == rb.employees_with_disability
        assert ra.workplace_accommodations_completed == rb.workplace_accommodations_completed
        assert ra.workplace_accommodations_requested == rb.workplace_accommodations_requested
        pct_a, pct_b = ra.accessibility_training_completion_pct, rb.accessibility_training_completion_pct
        if math.isnan(pct_a) or math.isnan(pct_b):
            assert math.isnan(pct_a) and math.isnan(pct_b)
        else:
            assert pct_a == pct_b
        assert ra.source == rb.source


def test_different_seed_differs():
    a = generate_accessibility_records(seed=21)
    b = generate_accessibility_records(seed=22)
    assert a != b


def test_covers_all_departments_and_quarters():
    records = generate_accessibility_records()
    covered = {(r.department, r.quarter) for r in records}
    for dept in DEPARTMENTS:
        for quarter in QUARTERS:
            assert (dept, quarter) in covered


def test_injected_overcount_present():
    records = generate_accessibility_records()
    overcounts = [
        r for r in records
        if r.workplace_accommodations_completed > r.workplace_accommodations_requested
    ]
    assert len(overcounts) >= 1
    assert any(r.department == "Production" and r.quarter == "2026-Q1" for r in overcounts)


def test_injected_missing_training_metric_present():
    records = generate_accessibility_records()
    missing = [r for r in records if math.isnan(r.accessibility_training_completion_pct)]
    assert len(missing) >= 1
    assert any(r.department == "Flight Test" and r.quarter == "2026-Q2" for r in missing)


def test_headcounts_are_positive():
    records = generate_accessibility_records()
    assert all(r.headcount > 0 for r in records)


def test_employees_with_disability_never_exceeds_headcount():
    records = generate_accessibility_records()
    assert all(r.employees_with_disability <= r.headcount for r in records)


def test_performance_records_cover_all_departments_and_quarters():
    records = generate_department_performance_records()
    covered = {(r.department, r.quarter) for r in records}
    for dept in DEPARTMENTS:
        for quarter in QUARTERS:
            assert (dept, quarter) in covered


def test_performance_metrics_in_plausible_ranges():
    records = generate_department_performance_records()
    for r in records:
        assert 0 <= r.on_time_delivery_pct <= 100
        assert 1 <= r.employee_engagement_score <= 5
        assert 0 <= r.voluntary_attrition_pct <= 100
