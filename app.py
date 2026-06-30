import uuid
from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session-state initialisation
# st.session_state is a dict-like vault that survives reruns within one
# browser session.  We check "owner" in st.session_state before creating a
# new Owner so we don't reset the user's data every time the script reruns.
# ---------------------------------------------------------------------------
DATA_FILE = "data.json"

if "owner" not in st.session_state:
    # Attempt to restore a previous session from disk on first load
    st.session_state.owner = Owner.load_from_json(DATA_FILE)

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.header("1. Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Alex Rivera")
    time_budget = st.number_input(
        "Daily time available (minutes)", min_value=10, max_value=480, value=90
    )
    windows = st.multiselect(
        "Preferred time windows",
        ["morning", "afternoon", "evening"],
        default=["morning", "evening"],
    )
    submitted_owner = st.form_submit_button("Save Owner")

if submitted_owner:
    # Replace (or create) the Owner stored in session_state
    st.session_state.owner = Owner(
        name=owner_name,
        daily_time_available_minutes=int(time_budget),
        preferred_time_windows=windows,
    )
    # Preserve any pets that were added to a previous Owner object
    if "pets_backup" in st.session_state:
        for pet in st.session_state.pets_backup:
            st.session_state.owner.add_pet(pet)
    st.session_state.owner.save_to_json(DATA_FILE)
    st.success(f"Owner '{owner_name}' saved with {time_budget} min/day.")

owner: Owner | None = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet
# ---------------------------------------------------------------------------
st.header("2. Add a Pet")

if owner is None:
    st.info("Save your owner info above first.")
else:
    with st.form("pet_form"):
        pet_name = st.text_input("Pet name", value="Buddy")
        species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        breed = st.text_input("Breed", value="Labrador")
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        energy = st.selectbox("Energy level", ["low", "medium", "high"], index=2)
        health = st.text_input("Health notes (optional)", value="")
        submitted_pet = st.form_submit_button("Add Pet")

    if submitted_pet:
        new_pet = Pet(
            name=pet_name,
            species=species,
            breed=breed,
            age=int(age),
            energy_level=energy,
            health_notes=health,
        )
        # owner.add_pet() appends to owner.pets so the UI reflects the change
        # on the very next rerun without any extra state management.
        owner.add_pet(new_pet)
        # Keep a backup so pets survive an owner-form resubmit
        st.session_state.pets_backup = owner.get_pets()
        owner.save_to_json(DATA_FILE)
        st.success(f"Added {pet_name} the {species}!")

    if owner.get_pets():
        st.write("**Your pets:**")
        for pet in owner.get_pets():
            st.markdown(f"- {pet.get_care_needs_summary()}")
    else:
        st.info("No pets added yet.")

# ---------------------------------------------------------------------------
# Section 3 — Add a Task
# ---------------------------------------------------------------------------
st.header("3. Add a Task")

if owner is None or not owner.get_pets():
    st.info("Add at least one pet before adding tasks.")
else:
    with st.form("task_form"):
        target_pet_name = st.selectbox(
            "Assign to pet", [p.name for p in owner.get_pets()]
        )
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox(
            "Category", ["exercise", "feeding", "medical", "grooming", "enrichment", "other"]
        )
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurrence = st.selectbox("Recurrence", ["daily", "weekly", "once"])
        mandatory = st.checkbox("Mandatory task?")
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        # Find the Pet object whose name matches the selectbox choice
        target_pet = next(p for p in owner.get_pets() if p.name == target_pet_name)
        task = Task(
            task_id=str(uuid.uuid4())[:8],
            title=task_title,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            pet_name=target_pet_name,
            recurrence=recurrence,
            mandatory=mandatory,
        )
        # Pet.tasks is a plain list — appending here is all that's needed;
        # the Scheduler reads pet.tasks directly when generating a plan.
        target_pet.tasks.append(task)
        owner.save_to_json(DATA_FILE)
        st.success(f"Task '{task_title}' added to {target_pet_name}.")

    # Show all tasks grouped by pet — sorted chronologically, conflicts highlighted
    scheduler = Scheduler()
    for pet in owner.get_pets():
        if not pet.tasks:
            continue

        st.write(f"**{pet.name}'s tasks:**")

        sorted_tasks = scheduler.sort_by_time(pet.tasks)

        # Conflict warnings — shown before the table so the owner sees them immediately
        conflicts = scheduler.detect_conflicts(pet.tasks)
        for warning in conflicts:
            st.warning(f"⚠️ **Scheduling conflict detected:** {warning}\n\n"
                       "Two tasks share the same time slot. "
                       "Edit one task's time below so they don't overlap.")

        pending = scheduler.filter_tasks(sorted_tasks, completed=False)
        done    = scheduler.filter_tasks(sorted_tasks, completed=True)

        rows = [
            {
                "Time": t.time or "—",
                "Title": t.title,
                "Category": t.category,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Recurrence": t.recurrence,
                "Mandatory": "✅" if t.mandatory else "",
            }
            for t in pending
        ]
        st.table(rows)

        if done:
            with st.expander(f"Completed tasks ({len(done)})"):
                st.table([{"Title": t.title, "Category": t.category} for t in done])

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule
# ---------------------------------------------------------------------------
st.header("4. Generate Today's Schedule")

if owner is None or not owner.get_pets():
    st.info("Set up an owner and at least one pet to generate a schedule.")
else:
    all_tasks = Scheduler().get_all_tasks(owner)
    if not all_tasks:
        st.info("Add some tasks first.")
    elif st.button("Generate schedule"):
        scheduler = Scheduler(strategy="priority_first")
        today = date.today()

        for pet in owner.get_pets():
            if not pet.tasks:
                continue
            plan = scheduler.generate_plan(pet.tasks, owner, pet, today)

            st.subheader(f"📋 {pet.name}'s Plan — {today.strftime('%A, %B %d')}")

            # ── Conflict check on the scheduled items ──────────────────────
            scheduled_tasks = [item["task"] for item in plan.scheduled_items]
            conflicts = scheduler.detect_conflicts(scheduled_tasks)
            for warning in conflicts:
                st.warning(
                    f"⚠️ **Time conflict in today's plan:** {warning}\n\n"
                    "Two tasks are scheduled at the same time. "
                    "Return to Section 3 to assign different times, "
                    "or reduce task count to fit within your time budget."
                )

            # ── Scheduled tasks — sorted chronologically ───────────────────
            if plan.scheduled_items:
                sorted_items = sorted(
                    plan.scheduled_items,
                    key=lambda item: item["start_time"]
                )
                total_min = plan.total_time()
                budget = owner.daily_time_available_minutes
                st.success(
                    f"✅ Scheduled {len(sorted_items)} task(s) — "
                    f"{total_min} of {budget} min used "
                    f"({budget - total_min} min remaining)"
                )
                rows = [
                    {
                        "Time": item["start_time"].strftime("%H:%M"),
                        "Task": item["task"].title,
                        "Category": item["task"].category,
                        "Duration (min)": item["task"].duration_minutes,
                        "Priority": item["task"].priority,
                        "Mandatory": "✅" if item["task"].mandatory else "",
                    }
                    for item in sorted_items
                ]
                st.table(rows)
            else:
                st.warning("⚠️ No tasks could be scheduled. Check your time budget in Section 1.")

            # ── Tasks that didn't fit ───────────────────────────────────────
            if plan.unscheduled_tasks:
                with st.expander(f"⏭️ Skipped tasks ({len(plan.unscheduled_tasks)}) — click to expand"):
                    for item in plan.unscheduled_tasks:
                        st.markdown(f"- **{item['task'].title}** — _{item['reason']}_")

            # ── Scheduler reasoning ────────────────────────────────────────
            with st.expander("🧠 Scheduler reasoning"):
                st.text(plan.explain_choices())
