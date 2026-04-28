---
name: deadline-risk-planner
description: Parses a pasted task list or CSV file of assignments, validates due dates and required fields, computes time remaining and workload risk, and returns a prioritized study plan. Use when the user asks to organize assignments, calculate urgency, audit deadlines, or turn a task list into a schedule.
---

# Deadline Risk Planner

## When to use this skill
Use this skill when a user provides a list of assignments, projects, or tasks and wants a reliable deadline-based plan. This skill is especially useful when the user needs exact date calculations, workload prioritization, or a structured report from a CSV file.

Good requests include:
- "Plan my assignments from this CSV."
- "Which homework should I do first based on due dates and estimated hours?"
- "Check this task list and make a priority schedule."
- "Calculate how many days I have left for each assignment."

## When not to use this skill
Do not use this skill for broad life advice, emotional coaching, or open-ended productivity tips when there is no task list, due date, or estimated workload to calculate. Also do not use it for tasks that require calendar access or real-time scheduling with external systems.

## Expected input
The user should provide either:
1. A CSV file, or
2. Pasted CSV-style text

Required columns:
- `task`: name of the task or assignment
- `due_date`: due date in `YYYY-MM-DD` format
- `estimated_hours`: estimated number of hours required

Optional columns:
- `course`: class or project name
- `status`: not started, in progress, done
- `importance`: low, medium, high

## Script usage
Run the script inside `scripts/`:

```bash
python scripts/deadline_planner.py --input sample_data/tasks.csv --today 2026-04-28
```

Optional flags:

```bash
python scripts/deadline_planner.py --input sample_data/tasks.csv --today 2026-04-28 --output plan_report.md
```

## What the script does
The Python script performs the deterministic part of the workflow:
- reads and parses the CSV file
- validates required columns
- checks date format
- calculates days remaining from today's date
- calculates urgency and workload risk
- sorts tasks by priority
- formats a clear Markdown report

This code is load-bearing because a language model may make mistakes with date math, sorting, missing values, and repeatable risk scoring. The script makes those steps deterministic and reproducible.

## Expected output
The final output should include:
- a validation summary
- a prioritized task table
- risk labels such as `overdue`, `high`, `medium`, or `low`
- a short recommendation about what to do first
- any warnings for missing fields or invalid dates

## Limitations and checks
- The script does not connect to Google Calendar or Canvas.
- It assumes due dates use `YYYY-MM-DD`.
- Estimated hours must be numeric.
- The final study advice should be reviewed by the user because personal energy, class difficulty, and grading weight may change the plan.
