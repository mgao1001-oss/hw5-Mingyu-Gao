# hw5-Mingyu-Gao
# Deadline Risk Planner

## What this skill does
This skill analyzes tasks from a CSV file and evaluates their urgency based on deadlines and importance. It helps users identify high-risk tasks that need immediate attention.

## Why I chose it
I chose this skill because deadline management is a common real-world problem for students. This task requires deterministic computation (date calculation and scoring), which cannot be reliably handled by a prompt alone.

## How to use it
Provide a CSV file with the required columns:
- task
- due_date
- estimated_hours
- importance

Then run the script to generate a risk report.

## What the script does
The Python script:
- parses and validates the CSV file
- calculates days remaining for each task
- assigns a risk score and label
- outputs a structured report

## What worked well
The script reliably computes deadlines and assigns risk levels. It integrates well with the skill structure and demonstrates clear separation between model reasoning and deterministic logic.

## Limitations
- Requires strict CSV format
- Does not handle timezone differences
- Risk scoring is simplified and could be improved

## Demo Video
https://youtu.be/gFL6B_xOX00
