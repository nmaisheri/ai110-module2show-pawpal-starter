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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
