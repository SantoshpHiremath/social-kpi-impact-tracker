from src.data_sources import AccessibilityRecord
from src.data_quality import (
    find_accommodation_overcounts, find_missing_training_metrics, run_all_checks,
)


def make_record(**overrides):
    defaults = dict(
        department="Engineering Strategy", quarter="2025-Q1", headcount=100,
        employees_with_disability=6, workplace_accommodations_completed=3,
        workplace_accommodations_requested=4, accessibility_training_completion_pct=80.0,
        source="HR Quarterly Report",
    )
    defaults.update(overrides)
    return AccessibilityRecord(**defaults)


def test_no_flags_on_clean_record():
    r = make_record()
    assert find_accommodation_overcounts([r]) == []
    assert find_missing_training_metrics([r]) == []


def test_flags_overcount():
    r = make_record(workplace_accommodations_completed=5, workplace_accommodations_requested=3)
    flags = find_accommodation_overcounts([r])
    assert len(flags) == 1
    assert flags[0].issue_type == "accommodation_overcount"
    assert "5 completed exceeds 3 requested" in flags[0].detail


def test_does_not_flag_equal_completed_and_requested():
    r = make_record(workplace_accommodations_completed=4, workplace_accommodations_requested=4)
    assert find_accommodation_overcounts([r]) == []


def test_flags_missing_training_metric():
    r = make_record(accessibility_training_completion_pct=float("nan"))
    flags = find_missing_training_metrics([r])
    assert len(flags) == 1
    assert flags[0].issue_type == "missing_training_metric"


def test_run_all_checks_combines_both():
    overcount_record = make_record(
        department="A", workplace_accommodations_completed=9, workplace_accommodations_requested=6
    )
    missing_record = make_record(
        department="B", accessibility_training_completion_pct=float("nan")
    )
    clean_record = make_record(department="C")
    flags = run_all_checks([overcount_record, missing_record, clean_record])
    assert len(flags) == 2
    issue_types = {f.issue_type for f in flags}
    assert issue_types == {"accommodation_overcount", "missing_training_metric"}


def test_real_generated_data_flags_expected_count():
    from src.data_sources import generate_accessibility_records
    records = generate_accessibility_records()
    flags = run_all_checks(records)
    # exactly the two deliberately-injected issues should be caught
    assert len(flags) == 2
