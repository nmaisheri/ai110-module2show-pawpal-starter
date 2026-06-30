# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The three core actions the user should be able to perform are :
    1. Enter owner and pet information
    2. Add or edit pet care tasks (at least durating and priority)
    3. Be able to generate and view a daily care scedule or plan, which shold ideally have reasoning behind it.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
No, my design did not change during implementation
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three main constraints:

1. **Time budget** — the owner's `daily_time_available_minutes` acts as a hard cap. Tasks are selected greedily in priority order until the budget is exhausted; any task that doesn't fit is moved to `unscheduled_tasks` with the reason "insufficient time remaining."

2. **Priority and mandatory status** — each task is ranked by `priority_score()`, which combines a 1–3 base score (low/medium/high) with a +2 bonus for mandatory tasks. This ensures critical care (e.g., Luna's inhaler treatment) is always scheduled before optional enrichment activities.

3. **Recurrence and due date** — only tasks that are actually due on the target date are considered, filtered by `is_due_on()`. Daily tasks are always included; weekly and one-off tasks are only included when their date matches.

Priority and mandatory status were treated as the most important constraints because pet health and safety tasks (medical, mandatory walks) should never be bumped by lower-stakes activities regardless of time pressure. Time budget was kept as a hard constraint rather than a soft one to reflect a realistic owner who cannot exceed their available hours — tasks that don't fit are surfaced explicitly rather than silently dropped.

**b. Tradeoffs**

`detect_conflicts` checks for exact `time` string matches (e.g., both tasks have `time="07:00"`) rather than checking whether two tasks' durations overlap on a continuous timeline. This means a 60-minute task starting at 07:00 and a 30-minute task starting at 07:45 would not be flagged as a conflict, even though they overlap between 07:45 and 08:00.

This tradeoff is reasonable for the current scope of PawPal+ because tasks are entered with explicit start times by the owner, and the primary goal is to catch obvious double-bookings (two tasks assigned to the exact same slot) rather than to simulate a precise minute-by-minute calendar. An overlap-aware check would require converting `"HH:MM"` strings to `datetime` objects, computing end times using `duration_minutes`, and comparing intervals — meaningfully more complex logic for a use case where most conflicts arise from careless duplicate scheduling rather than tight back-to-back packing. If the scheduler were extended to auto-assign start times (rather than relying on user-provided ones), duration-based overlap detection would become the right default.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools throughout multiple phases of this project. During design, I described the scheduling scenario and asked the assistant to help me identify what classes and relationships would be needed before writing any code. During implementation, I used it to debug logic in `mark_task_complete` and `detect_conflicts`, and to generate the initial test stubs for the three key behaviors (sorting, recurrence, conflict detection). The most helpful prompts were specific and grounded in the actual code — for example, "given this Task dataclass, write a test that verifies a daily task creates a next-day occurrence when marked complete" produced directly usable output, whereas vague prompts like "help me test my scheduler" required several follow-ups before the output was useful.

**b. Judgment and verification**

When the AI first drafted the `detect_conflicts` method, it suggested using a full datetime interval overlap check — converting each task's `time` string to a `datetime`, adding `duration_minutes`, and comparing ranges. I did not accept this as-is because the task form in the UI doesn't yet enforce that every task has a time, so many tasks have `time=None`. An interval-based check would either crash on `None` values or silently skip tasks, making it less reliable than a simple exact-match check for this stage of the project. I evaluated the suggestion by tracing through what would happen when a user adds a task without specifying a time — the interval version would raise a `TypeError` on `None + timedelta`. I kept the exact-match approach and documented the tradeoff explicitly in section 2b above.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers three core behaviors:

1. **Sorting correctness** — `sort_by_time` returns tasks in chronological `HH:MM` order, tasks with no time value sort last, and identical times don't raise an error or reorder unpredictably.

2. **Recurrence logic** — completing a daily task via `mark_task_complete` appends a new Task to the pet with `due_date_or_day` set to tomorrow, the original task is marked `completed=True`, and one-off tasks (`recurrence="once"`) produce no new occurrence.

3. **Conflict detection** — `detect_conflicts` flags two tasks sharing the same time slot, produces no warnings when times differ, excludes completed tasks and tasks with no time set, and correctly generates all pairwise warnings when three tasks share the same slot.

These tests were important because they cover the three features added in Phase 2 that the existing codebase had no coverage for. Sorting and conflict detection are the main user-facing safety features — a pet owner relying on the schedule needs tasks to appear in time order and needs to be told when two tasks would clash. Recurrence logic is the most stateful behavior in the system: it mutates `pet.tasks` and generates new objects, so a bug there could silently cause tasks to be missed or duplicated across days.

**b. Confidence**

Confidence level: **4 out of 5**. The unit tests confirm that each method behaves correctly in isolation for both happy paths and the most likely edge cases. The main gap is integration coverage — there are no tests that run a full `generate_plan` round-trip with a real `Owner`, `Pet`, and multiple tasks to verify that the plan's `scheduled_items` and `unscheduled_tasks` are populated correctly end-to-end. The Streamlit UI layer is also untested.

If I had more time, the next edge cases to test would be:
- A pet whose tasks total exactly the owner's time budget (boundary condition on `select_tasks_within_time_limit`)
- A weekly recurring task checked on the wrong day of the week — should not appear in the plan
- `mark_task_complete` called on a task that is already completed — should not append a second next-occurrence
- An owner with `daily_time_available_minutes=0` — the scheduler should produce a plan with no scheduled tasks and all tasks in `unscheduled_tasks`

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is how cleanly the `Scheduler` class ended up handling multiple concerns without becoming a mess. `detect_conflicts`, `sort_by_time`, `filter_tasks`, and `mark_task_complete` each do exactly one thing and are easy to test in isolation — the 13-test suite covers all of them with no mocking needed because none of them have hidden dependencies. The fact that `mark_task_complete` uses `dataclasses.replace()` to clone a task into its next occurrence was a good design call: it means new fields added to `Task` in the future are inherited automatically without needing to update the recurrence logic.

**b. What you would improve**

The main thing I would redesign is the conflict detection model. Right now `detect_conflicts` flags tasks that share the exact same `"HH:MM"` start time, which catches obvious double-bookings but misses overlapping tasks — a 60-minute task at 07:00 and a 30-minute task at 07:45 collide between 07:45 and 08:00 and are never flagged. Moving to duration-aware interval overlap (convert `"HH:MM"` + `duration_minutes` to a `datetime` range and check `start_a < end_b and start_b < end_a`) would make the scheduler meaningfully more reliable. I would also add a `time` input field to the task form in the UI — right now tasks can only get a time value programmatically, so the conflict detection feature is mostly invisible to a user who adds tasks through the Streamlit UI.

**c. Key takeaway**

The most important thing I learned is that AI tools are most useful when you already have a clear mental model of what you're building. When I came in with a specific question — "given this dataclass, write a test that verifies recurrence creates a next-day task" — the output was directly usable. When I asked something open-ended before thinking it through myself, I had to spend time filtering suggestions that technically worked but didn't fit the constraints I hadn't stated yet (like the interval-overlap conflict detection that broke on `None` times). Designing first and using AI to accelerate execution is more effective than using AI to do the designing.
