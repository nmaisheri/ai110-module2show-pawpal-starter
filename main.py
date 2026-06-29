from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

today = date.today()

# --- Owner ---
owner = Owner(
    name="Alex Rivera",
    daily_time_available_minutes=90,
    preferred_time_windows=["morning", "evening"],
)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3, energy_level="high")
luna = Pet(name="Luna", species="Cat", breed="Siamese", age=5, energy_level="medium", health_notes="asthma")

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Tasks added OUT OF ORDER (later times first) ---
buddy.tasks.append(Task(
    task_id="b2",
    title="Fetch & Play",
    category="exercise",
    duration_minutes=20,
    priority="medium",
    pet_name="Buddy",
    recurrence="daily",
    time="15:30",
))
buddy.tasks.append(Task(
    task_id="b3",
    title="Evening Walk",
    category="exercise",
    duration_minutes=25,
    priority="high",
    pet_name="Buddy",
    recurrence="daily",
    mandatory=True,
    time="18:00",
    completed=True,
))
buddy.tasks.append(Task(
    task_id="b1",
    title="Morning Walk",
    category="exercise",
    duration_minutes=30,
    priority="high",
    pet_name="Buddy",
    recurrence="daily",
    mandatory=True,
    time="07:00",
))

luna.tasks.append(Task(
    task_id="l3",
    title="Interactive Toy Session",
    category="enrichment",
    duration_minutes=25,
    priority="medium",
    pet_name="Luna",
    recurrence="daily",
    time="17:00",
))
luna.tasks.append(Task(
    task_id="l1",
    title="Inhaler Treatment",
    category="medical",
    duration_minutes=10,
    priority="high",
    pet_name="Luna",
    recurrence="daily",
    mandatory=True,
    time="08:00",
))
luna.tasks.append(Task(
    task_id="l2",
    title="Brush Coat",
    category="grooming",
    duration_minutes=15,
    priority="low",
    pet_name="Luna",
    recurrence="daily",
    time="12:00",
    completed=True,
))

# --- Intentional conflicts to test detection ---
# Both tasks are at 07:00, same as Morning Walk (b1) — one same-pet, one cross-pet.
buddy.tasks.append(Task(
    task_id="b4",
    title="Vet Appointment",
    category="medical",
    duration_minutes=60,
    priority="high",
    pet_name="Buddy",
    recurrence="once",
    due_date_or_day=today,
    time="07:00",  # conflicts with Morning Walk (b1)
))
luna.tasks.append(Task(
    task_id="l4",
    title="Grooming Appointment",
    category="grooming",
    duration_minutes=45,
    priority="medium",
    pet_name="Luna",
    recurrence="once",
    due_date_or_day=today,
    time="07:00",  # conflicts with Morning Walk (b1) across pets
))

# --- Scheduler ---
scheduler = Scheduler(strategy="priority_first")
all_tasks = scheduler.get_all_tasks(owner)

# ── Daily plan (existing behavior) ───────────────────────────────────────────
print("=" * 50)
print(f"  TODAY'S SCHEDULE  —  {today.strftime('%A, %B %d %Y')}")
print(f"  Owner: {owner.name}  |  Time budget: {owner.daily_time_available_minutes} min")
print("=" * 50)

for pet in owner.get_pets():
    plan = scheduler.generate_plan(pet.tasks, owner, pet, today)
    print(plan.to_display_format())
    print()
    print("  Reasoning:")
    for line in plan.explanation_log:
        print(f"    {line}")
    print("-" * 50)

print(f"\nAll tasks across all pets: {len(all_tasks)} total")

# ── Auto-recurrence demo ──────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  MARKING TASKS COMPLETE  (auto-recurrence)")
print("=" * 50)

# Mark Buddy's Morning Walk and Luna's Inhaler Treatment complete.
# Both are "daily", so the scheduler should create tomorrow's instances automatically.
morning_walk = next(t for t in buddy.tasks if t.task_id == "b1")
inhaler = next(t for t in luna.tasks if t.task_id == "l1")

next_walk = scheduler.mark_task_complete(morning_walk, buddy)
next_inhaler = scheduler.mark_task_complete(inhaler, luna)

print(f"  Completed : '{morning_walk.title}' for {morning_walk.pet_name} — completed={morning_walk.completed}")
if next_walk:
    print(f"  Next due  : '{next_walk.title}' on {next_walk.due_date_or_day} (id={next_walk.task_id})")

print()
print(f"  Completed : '{inhaler.title}' for {inhaler.pet_name} — completed={inhaler.completed}")
if next_inhaler:
    print(f"  Next due  : '{next_inhaler.title}' on {next_inhaler.due_date_or_day} (id={next_inhaler.task_id})")

# Also mark Fetch & Play complete (daily) and verify new task appears for Buddy
fetch = next(t for t in buddy.tasks if t.task_id == "b2")
next_fetch = scheduler.mark_task_complete(fetch, buddy)
print()
print(f"  Completed : '{fetch.title}' for {fetch.pet_name} — completed={fetch.completed}")
if next_fetch:
    print(f"  Next due  : '{next_fetch.title}' on {next_fetch.due_date_or_day} (id={next_fetch.task_id})")

# ── sort_by_time demo ─────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  ALL TASKS SORTED BY TIME (HH:MM)")
print("=" * 50)
sorted_tasks = scheduler.sort_by_time(all_tasks)
for t in sorted_tasks:
    status = "[DONE]" if t.completed else "[ ]  "
    print(f"  {status} {t.time or 'N/A':>5}  {t.pet_name:<8}  {t.title}")

# ── filter_tasks demo ─────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  INCOMPLETE TASKS ONLY")
print("=" * 50)
incomplete = scheduler.filter_tasks(all_tasks, completed=False)
for t in scheduler.sort_by_time(incomplete):
    print(f"  {t.time or 'N/A':>5}  {t.pet_name:<8}  {t.title}")

print("\n" + "=" * 50)
print("  BUDDY'S TASKS ONLY")
print("=" * 50)
buddy_tasks = scheduler.filter_tasks(all_tasks, pet_name="Buddy")
for t in scheduler.sort_by_time(buddy_tasks):
    status = "[DONE]" if t.completed else "[ ]  "
    print(f"  {status} {t.time or 'N/A':>5}  {t.title}")

print("\n" + "=" * 50)
print("  COMPLETED TASKS ONLY")
print("=" * 50)
done = scheduler.filter_tasks(all_tasks, completed=True)
for t in scheduler.sort_by_time(done):
    print(f"  {t.time or 'N/A':>5}  {t.pet_name:<8}  {t.title}")

# ── Conflict detection demo ───────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  CONFLICT DETECTION")
print("=" * 50)
all_tasks_refreshed = scheduler.get_all_tasks(owner)
conflicts = scheduler.detect_conflicts(all_tasks_refreshed)
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No scheduling conflicts found.")
