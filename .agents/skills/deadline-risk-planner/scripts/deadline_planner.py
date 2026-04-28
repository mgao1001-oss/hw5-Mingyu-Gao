#!/usr/bin/env python3
"""
Deadline Risk Planner

This script parses an assignment/task CSV, validates the structure,
calculates days remaining, assigns risk levels, and generates a Markdown report.
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import List, Tuple

REQUIRED_COLUMNS = {"task", "due_date", "estimated_hours"}
VALID_IMPORTANCE = {"low", "medium", "high", ""}


@dataclass
class TaskResult:
    task: str
    course: str
    due_date: date
    estimated_hours: float
    status: str
    importance: str
    days_remaining: int
    risk_score: float
    risk_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a deadline-based task priority report.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--today", default=None, help="Optional date override in YYYY-MM-DD format.")
    parser.add_argument("--output", default=None, help="Optional path for Markdown report output.")
    return parser.parse_args()


def parse_today(today_arg: str | None) -> date:
    if today_arg:
        return datetime.strptime(today_arg, "%Y-%m-%d").date()
    return date.today()


def load_rows(path: Path) -> Tuple[List[dict], List[str]]:
    warnings: List[str] = []
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    if not rows:
        warnings.append("The CSV file is empty.")
    return rows, warnings


def compute_risk(days_remaining: int, estimated_hours: float, importance: str, status: str) -> Tuple[float, str]:
    if status.lower().strip() == "done":
        return 0.0, "done"
    if days_remaining < 0:
        return 100.0, "overdue"

    urgency_score = max(0, 30 - days_remaining * 5)
    workload_score = min(40, estimated_hours * 4)
    importance_score = {"high": 25, "medium": 12, "low": 5, "": 8}.get(importance.lower().strip(), 8)
    risk_score = urgency_score + workload_score + importance_score

    if risk_score >= 70:
        label = "high"
    elif risk_score >= 40:
        label = "medium"
    else:
        label = "low"
    return round(risk_score, 1), label


def process_rows(rows: List[dict], today: date) -> Tuple[List[TaskResult], List[str]]:
    results: List[TaskResult] = []
    warnings: List[str] = []

    for idx, row in enumerate(rows, start=2):
        task = (row.get("task") or "").strip()
        due_date_raw = (row.get("due_date") or "").strip()
        hours_raw = (row.get("estimated_hours") or "").strip()
        course = (row.get("course") or "General").strip() or "General"
        status = (row.get("status") or "not started").strip() or "not started"
        importance = (row.get("importance") or "medium").strip().lower()

        if not task:
            warnings.append(f"Row {idx}: missing task name; row skipped.")
            continue

        try:
            due = datetime.strptime(due_date_raw, "%Y-%m-%d").date()
        except ValueError:
            warnings.append(f"Row {idx} ({task}): invalid due_date '{due_date_raw}'; row skipped.")
            continue

        try:
            hours = float(hours_raw)
            if hours < 0:
                raise ValueError
        except ValueError:
            warnings.append(f"Row {idx} ({task}): estimated_hours must be a non-negative number; row skipped.")
            continue

        if importance not in VALID_IMPORTANCE:
            warnings.append(f"Row {idx} ({task}): unknown importance '{importance}', treated as medium.")
            importance = "medium"

        days_remaining = (due - today).days
        risk_score, risk_label = compute_risk(days_remaining, hours, importance, status)

        results.append(TaskResult(
            task=task,
            course=course,
            due_date=due,
            estimated_hours=hours,
            status=status,
            importance=importance or "medium",
            days_remaining=days_remaining,
            risk_score=risk_score,
            risk_label=risk_label,
        ))

    results.sort(key=lambda r: (-r.risk_score, r.due_date, -r.estimated_hours))
    return results, warnings


def format_report(results: List[TaskResult], warnings: List[str], today: date) -> str:
    lines: List[str] = []
    lines.append("# Deadline Risk Planner Report")
    lines.append("")
    lines.append(f"Generated using today = `{today.isoformat()}`.")
    lines.append("")

    lines.append("## Validation Summary")
    lines.append(f"- Valid tasks analyzed: {len(results)}")
    lines.append(f"- Warnings: {len(warnings)}")
    if warnings:
        for warning in warnings:
            lines.append(f"  - {warning}")
    lines.append("")

    lines.append("## Prioritized Task List")
    lines.append("| Priority | Task | Course | Due Date | Days Left | Hours | Importance | Status | Risk |")
    lines.append("|---:|---|---|---|---:|---:|---|---|---|")
    for i, item in enumerate(results, start=1):
        lines.append(
            f"| {i} | {item.task} | {item.course} | {item.due_date.isoformat()} | "
            f"{item.days_remaining} | {item.estimated_hours:g} | {item.importance} | "
            f"{item.status} | {item.risk_label} ({item.risk_score}) |"
        )
    lines.append("")

    lines.append("## Recommendation")
    active = [r for r in results if r.risk_label not in {"done"}]
    if not active:
        lines.append("All listed tasks are marked as done or no valid tasks were provided.")
    else:
        first = active[0]
        lines.append(
            f"Start with **{first.task}** for **{first.course}** because it has the highest risk score "
            f"and is due in {first.days_remaining} day(s)."
        )
        high_count = sum(1 for r in active if r.risk_label in {"high", "overdue"})
        if high_count:
            lines.append(f"There are **{high_count}** high-risk or overdue task(s), so avoid spending time on low-risk work first.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    today = parse_today(args.today)
    rows, load_warnings = load_rows(input_path)
    results, process_warnings = process_rows(rows, today)
    report = format_report(results, load_warnings + process_warnings, today)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
