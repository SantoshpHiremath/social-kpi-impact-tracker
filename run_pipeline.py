"""
Runs the full Social KPI & Departmental Impact Tracker pipeline end to
end and prints a real console report.
"""

from src.data_sources import generate_accessibility_records, generate_department_performance_records
from src.data_quality import run_all_checks
from src.kpi_linkage import compute_accessibility_kpis, link_to_department_performance, program_progress_trend
from src.report import build_report


def main():
    access_records = generate_accessibility_records()
    perf_records = generate_department_performance_records()
    print(f"Loaded {len(access_records)} accessibility records and {len(perf_records)} performance records.")

    flags = run_all_checks(access_records)
    print(f"Data-quality check: {len(flags)} flag(s) raised.")
    for f in flags:
        print(f"  {f.issue_type.upper()}: {f.department} {f.quarter} — {f.detail}")

    kpis = compute_accessibility_kpis(access_records)
    linked = link_to_department_performance(kpis, perf_records)
    print(f"\nLinked {len(linked)} department/quarter accessibility-performance records.")

    print("\nAccessibility program progress trend — Engineering Strategy (training completion %):")
    trend = program_progress_trend(kpis, "Engineering Strategy")
    for quarter, pct in trend:
        display = f"{pct}%" if pct is not None else "not reported"
        print(f"  {quarter}: {display}")

    output_path = build_report(linked, flags)
    print(f"\nReport written to {output_path}")


if __name__ == "__main__":
    main()
