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

# --- Tasks for Buddy ---
buddy.tasks.append(Task(
    task_id="b1",
    title="Morning Walk",
    category="exercise",
    duration_minutes=30,
    priority="high",
    pet_name="Buddy",
    recurrence="daily",
    mandatory=True,
))
buddy.tasks.append(Task(
    task_id="b2",
    title="Fetch & Play",
    category="exercise",
    duration_minutes=20,
    priority="medium",
    pet_name="Buddy",
    recurrence="daily",
))

# --- Tasks for Luna ---
luna.tasks.append(Task(
    task_id="l1",
    title="Inhaler Treatment",
    category="medical",
    duration_minutes=10,
    priority="high",
    pet_name="Luna",
    recurrence="daily",
    mandatory=True,
))
luna.tasks.append(Task(
    task_id="l2",
    title="Brush Coat",
    category="grooming",
    duration_minutes=15,
    priority="low",
    pet_name="Luna",
    recurrence="daily",
))
luna.tasks.append(Task(
    task_id="l3",
    title="Interactive Toy Session",
    category="enrichment",
    duration_minutes=25,
    priority="medium",
    pet_name="Luna",
    recurrence="daily",
))

# --- Scheduler ---
scheduler = Scheduler(strategy="priority_first")
all_tasks = scheduler.get_all_tasks(owner)

# Group tasks by pet for per-pet plans, then print a combined schedule
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
