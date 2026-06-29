# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python3 main.py` (two pets, five tasks, 90-minute owner budget):

```
==================================================
  TODAY'S SCHEDULE  —  Monday, June 29 2026
  Owner: Alex Rivera  |  Time budget: 90 min
==================================================
Daily Plan for Buddy on 2026-06-29 (owner: Alex Rivera)
  08:00 — Morning Walk (30 min)
  08:30 — Fetch & Play (20 min)

  Reasoning:
    Scheduled 'Morning Walk' (priority=high, 30 min) at 08:00
    Scheduled 'Fetch & Play' (priority=medium, 20 min) at 08:30
--------------------------------------------------
Daily Plan for Luna on 2026-06-29 (owner: Alex Rivera)
  08:00 — Inhaler Treatment (10 min)
  08:10 — Interactive Toy Session (25 min)
  08:35 — Brush Coat (15 min)

  Reasoning:
    Scheduled 'Inhaler Treatment' (priority=high, 10 min) at 08:00
    Scheduled 'Interactive Toy Session' (priority=medium, 25 min) at 08:10
    Scheduled 'Brush Coat' (priority=low, 15 min) at 08:35
--------------------------------------------------

All tasks across all pets: 5 total
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| **Time-based sorting** | `Scheduler.sort_by_time(tasks)` | Sorts tasks chronologically by their `time` field (`"HH:MM"` string). Uses a lambda key so lexicographic and clock order are identical for zero-padded strings. Tasks with no time value are placed last via the sentinel `"99:99"`. |
| **Filtering** | `Scheduler.filter_tasks(tasks, completed, pet_name)` | Narrows a task list by completion status (`True`/`False`), pet name, or both. Parameters are optional and composable — omitting one skips that filter axis entirely. |
| **Conflict detection** | `Scheduler.detect_conflicts(tasks)` | Performs a pairwise O(n²) scan over all pending timed tasks and returns a human-readable warning string for every pair that shares the same `time` slot. Never raises — returns an empty list when no conflicts exist. Completed tasks are excluded since they no longer occupy an active slot. |
| **Recurring task auto-creation** | `Scheduler.mark_task_complete(task, pet)` | Marks a task done and, for `"daily"` or `"weekly"` tasks, uses `timedelta` to compute the next due date (today + 1 day or + 7 days) and appends a fresh Task instance to the pet. One-off tasks (`recurrence="once"`) return `None`. Uses `dataclasses.replace()` to copy all fields safely, so new Task attributes are inherited automatically. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
