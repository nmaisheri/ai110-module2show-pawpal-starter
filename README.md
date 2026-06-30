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

### How to run

```bash
python3 -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests |
|------|-------|
| **Sorting correctness** | Tasks are returned in chronological `HH:MM` order; tasks with no time sort last; identical times don't raise and preserve insertion order. |
| **Recurrence logic** | Completing a daily task appends a new Task due the following day, the original is marked done, and one-off tasks produce no new occurrence. |
| **Conflict detection** | Duplicate time slots produce a warning string; different slots produce none; completed tasks and untimed tasks are excluded from checks; three tasks at the same slot yield all three pairwise warnings. |
| **Core task/pet behavior** | Marking complete flips `task.completed`; appending tasks increments `pet.tasks`. |

### Successful test run output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0 -- /Library/Frameworks/Python.framework/Versions/3.14/bin/python3
cachedir: .pytest_cache
rootdir: /Users/nmaisheri/Documents/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collecting ... collected 13 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  7%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 15%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 23%]
tests/test_pawpal.py::test_sort_by_time_tasks_without_time_go_last PASSED [ 30%]
tests/test_pawpal.py::test_sort_by_time_identical_times_preserves_input_order PASSED [ 38%]
tests/test_pawpal.py::test_mark_task_complete_creates_next_day_task_for_daily PASSED [ 46%]
tests/test_pawpal.py::test_mark_task_complete_original_is_marked_done PASSED [ 53%]
tests/test_pawpal.py::test_mark_task_complete_returns_none_for_one_off_task PASSED [ 61%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_time_slots PASSED [ 69%]
tests/test_pawpal.py::test_detect_conflicts_no_warnings_for_different_times PASSED [ 76%]
tests/test_pawpal.py::test_detect_conflicts_skips_completed_tasks PASSED [ 84%]
tests/test_pawpal.py::test_detect_conflicts_skips_tasks_without_time PASSED [ 92%]
tests/test_pawpal.py::test_detect_conflicts_three_tasks_same_slot_produces_three_warnings PASSED [100%]

============================== 13 passed in 0.01s ==============================
```

### Confidence Level

**★★★★☆ (4/5)**

The core scheduling behaviors — sorting, conflict detection, recurrence, and task completion — are all tested and passing. One star is held back because the tests cover unit-level logic but do not exercise the Streamlit UI layer or integration paths (e.g., a full `generate_plan` round-trip with a real Owner + Pet + multiple tasks). Adding integration and UI smoke tests would bring this to 5/5.

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
