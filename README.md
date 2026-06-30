# PawPal+ — Pet Care Scheduler

**PawPal+** is a Streamlit app that helps a pet owner stay consistent with daily pet care. Enter your pets, add tasks with priorities and durations, and let the scheduler build a time-budgeted daily plan — complete with conflict warnings, recurrence tracking, and a transparent reasoning log.

## Features

| Feature | How it works |
|---------|-------------|
| **Owner & pet profiles** | Store an owner's name, daily time budget (minutes), and preferred care windows (morning / afternoon / evening). Multiple pets are supported, each with their own task list. |
| **Task management** | Add tasks with title, category, duration, priority (low / medium / high), recurrence (daily / weekly / once), and an optional mandatory flag. Tasks are stored per-pet. |
| **Priority-first scheduling** | `Scheduler.generate_plan()` ranks tasks by `priority_score()` — a 1–3 base score plus a +2 bonus for mandatory tasks — then greedily selects tasks until the owner's time budget is exhausted. Higher-priority tasks (e.g., a mandatory inhaler treatment) are always placed before lower-priority ones regardless of order entered. |
| **Time-based sorting** | `Scheduler.sort_by_time()` sorts any task list chronologically by `"HH:MM"` string. Tasks without a time set are placed last via a `"99:99"` sentinel, so they never cause errors or silently move to the top. |
| **Conflict detection** | `Scheduler.detect_conflicts()` performs a pairwise scan of all pending, timed tasks and returns a plain-English warning for every pair sharing the same time slot. Warnings appear as orange `st.warning` banners directly above the affected table, naming both tasks and their shared time. |
| **Daily & weekly recurrence** | `Scheduler.mark_task_complete()` marks a task done and — for `"daily"` or `"weekly"` tasks — uses `dataclasses.replace()` + `timedelta` to append a new Task instance to the pet, due the next occurrence date. One-off tasks produce no successor. |
| **Composable filtering** | `Scheduler.filter_tasks()` narrows a task list by completion status, pet name, or both. The UI uses this to show pending tasks in the main table and collapse completed tasks into an expandable section. |
| **Scheduler reasoning log** | Every generated plan records a human-readable explanation of why each task was scheduled or skipped, exposed via a collapsible "Scheduler reasoning" expander in the UI. |
| **Budget summary** | After generating a plan, a `st.success` banner shows tasks scheduled, minutes used, and minutes remaining against the owner's daily budget. |

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

## 🖥️ CLI Demo Output

Output from running `python3 main.py` (two pets — Buddy and Luna — eight tasks, 90-minute owner budget):

```
==================================================
  TODAY'S SCHEDULE  —  Tuesday, June 30 2026
  Owner: Alex Rivera  |  Time budget: 90 min
==================================================
Daily Plan for Buddy on 2026-06-30 (owner: Alex Rivera)
  08:00 — Evening Walk (25 min)
  08:25 — Morning Walk (30 min)
  08:55 — Fetch & Play (20 min)
  [Not scheduled]
    - Vet Appointment: insufficient time remaining

  Reasoning:
    Scheduled 'Evening Walk' (priority=high, 25 min) at 08:00
    Scheduled 'Morning Walk' (priority=high, 30 min) at 08:25
    Scheduled 'Fetch & Play' (priority=medium, 20 min) at 08:55
    Skipped 'Vet Appointment': insufficient time remaining
--------------------------------------------------
Daily Plan for Luna on 2026-06-30 (owner: Alex Rivera)
  08:00 — Inhaler Treatment (10 min)
  08:10 — Interactive Toy Session (25 min)
  08:35 — Grooming Appointment (45 min)
  [Not scheduled]
    - Brush Coat: insufficient time remaining

  Reasoning:
    Scheduled 'Inhaler Treatment' (priority=high, 10 min) at 08:00
    Scheduled 'Interactive Toy Session' (priority=medium, 25 min) at 08:10
    Scheduled 'Grooming Appointment' (priority=medium, 45 min) at 08:35
    Skipped 'Brush Coat': insufficient time remaining
--------------------------------------------------

All tasks across all pets: 8 total

==================================================
  MARKING TASKS COMPLETE  (auto-recurrence)
==================================================
  Completed : 'Morning Walk' for Buddy — completed=True
  Next due  : 'Morning Walk' on 2026-07-01 (id=b1_next)

  Completed : 'Inhaler Treatment' for Luna — completed=True
  Next due  : 'Inhaler Treatment' on 2026-07-01 (id=l1_next)

  Completed : 'Fetch & Play' for Buddy — completed=True
  Next due  : 'Fetch & Play' on 2026-07-01 (id=b2_next)

==================================================
  ALL TASKS SORTED BY TIME (HH:MM)
==================================================
  [DONE] 07:00  Buddy     Morning Walk
  [ ]   07:00  Buddy     Vet Appointment
  [ ]   07:00  Luna      Grooming Appointment
  [DONE] 08:00  Luna      Inhaler Treatment
  [DONE] 12:00  Luna      Brush Coat
  [DONE] 15:30  Buddy     Fetch & Play
  [ ]   17:00  Luna      Interactive Toy Session
  [DONE] 18:00  Buddy     Evening Walk

==================================================
  INCOMPLETE TASKS ONLY
==================================================
  07:00  Buddy     Vet Appointment
  07:00  Luna      Grooming Appointment
  17:00  Luna      Interactive Toy Session

==================================================
  BUDDY'S TASKS ONLY
==================================================
  [DONE] 07:00  Morning Walk
  [ ]   07:00  Vet Appointment
  [DONE] 15:30  Fetch & Play
  [DONE] 18:00  Evening Walk

==================================================
  CONFLICT DETECTION
==================================================
  WARNING: 'Vet Appointment' (Buddy) and 'Morning Walk' (Buddy) are both scheduled at 07:00.
  WARNING: 'Vet Appointment' (Buddy) and 'Grooming Appointment' (Luna) are both scheduled at 07:00.
  WARNING: 'Morning Walk' (Buddy) and 'Grooming Appointment' (Luna) are both scheduled at 07:00.
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

Launch the app with:

```bash
streamlit run app.py
```

### UI sections and what you can do

**Section 1 — Owner Info**
Enter your name, how many minutes per day you have available for pet care, and your preferred time windows (morning, afternoon, evening). Click **Save Owner** to confirm. The owner profile persists across the session — you can update it at any time without losing your pets or tasks.

**Section 2 — Add a Pet**
Fill in your pet's name, species, breed, age, energy level, and any health notes. Click **Add Pet**. Multiple pets can be added; each appears as a summary line below the form (e.g., `Buddy (Dog, Labrador, age 3) — energy: high`).

**Section 3 — Add a Task**
Select which pet the task belongs to, then set a title, category (exercise / feeding / medical / grooming / enrichment / other), duration in minutes, priority (low / medium / high), recurrence (daily / weekly / once), and whether the task is mandatory. Click **Add Task**.

After adding tasks, the table below the form shows all pending tasks for each pet, **sorted chronologically by time**. If two tasks share the same time slot, an orange warning banner appears immediately above the table:

> ⚠️ **Scheduling conflict detected:** WARNING: 'Morning Walk' (Buddy) and 'Vet Appointment' (Buddy) are both scheduled at 07:00. Edit one task's time below so they don't overlap.

Completed tasks are collapsed into a labelled expander so they don't clutter the pending view.

**Section 4 — Generate Today's Schedule**
Click **Generate schedule**. For each pet the scheduler:
1. Filters tasks to only those due today (`is_due_on`)
2. Ranks them by `priority_score()` — mandatory tasks jump to the top
3. Greedily selects tasks until the owner's time budget is exhausted
4. Displays a green success banner: `✅ Scheduled 3 task(s) — 75 of 90 min used (15 min remaining)`
5. Shows the scheduled tasks in a time-ordered table
6. Lists any skipped tasks (with reason) in a collapsible expander
7. Exposes the full scheduler reasoning log in a second expander

If two scheduled tasks share the same time slot, a conflict warning also appears here with instructions to fix the times in Section 3.

---

### Example workflow

1. **Save owner** — Alex Rivera, 90 min/day, morning + evening windows
2. **Add pet** — Buddy the Dog, high energy
3. **Add three tasks** for Buddy:
   - Morning Walk · 30 min · high priority · daily
   - Fetch & Play · 20 min · medium priority · daily
   - Vet Appointment · 60 min · high priority · once (today's date)
4. **Observe** — Section 3 shows all three tasks sorted by time. If Morning Walk and Vet Appointment share the same time slot, an orange conflict warning appears.
5. **Generate schedule** — The scheduler fits Morning Walk (30 min) and Fetch & Play (20 min) within the 90-minute budget. Vet Appointment (60 min) is skipped with "insufficient time remaining" — it would exceed the budget combined with the other two high-priority tasks.
6. **Read the reasoning** — Expand "Scheduler reasoning" to see exactly why each task was scheduled or skipped.

### Key Scheduler behaviors visible in the UI

| Behavior | Where you see it |
|----------|-----------------|
| Priority-first selection | Higher-priority tasks always appear before lower-priority ones in the schedule table |
| Time-based sorting | Task table in Section 3 is always in `HH:MM` order; untimed tasks appear last |
| Conflict warnings | Orange `st.warning` banners in Section 3 and Section 4 when two tasks share a time slot |
| Budget summary | Green `st.success` banner after generation showing minutes used vs. available |
| Skipped tasks | Collapsed expander labeled "Skipped tasks (N)" lists tasks that didn't fit and why |
| Completed tasks | Collapsed expander in Section 3 keeps the pending view clean |
| Scheduler reasoning | Collapsed expander in Section 4 shows the full decision log |
