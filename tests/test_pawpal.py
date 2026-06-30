from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(
    task_id="t1",
    title="Test Task",
    duration=15,
    priority="medium",
    recurrence="daily",
    time=None,
    pet_name=None,
):
    return Task(
        task_id=task_id,
        title=title,
        category="exercise",
        duration_minutes=duration,
        priority=priority,
        recurrence=recurrence,
        time=time,
        pet_name=pet_name,
    )


def make_pet(name="Buddy"):
    return Pet(name=name, species="Dog", breed="Labrador", age=3)


def make_owner(minutes=90):
    return Owner(name="Alex", daily_time_available_minutes=minutes)


# ---------------------------------------------------------------------------
# Existing tests (kept as-is)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.tasks.append(make_task("t1", "Morning Walk"))
    pet.tasks.append(make_task("t2", "Feeding"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness — tasks come back in chronological (HH:MM) order
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler()
    tasks = [
        make_task("t3", "Evening Walk", time="18:00"),
        make_task("t1", "Morning Feed", time="08:00"),
        make_task("t2", "Afternoon Meds", time="13:30"),
    ]
    result = scheduler.sort_by_time(tasks)
    times = [t.time for t in result]
    assert times == ["08:00", "13:30", "18:00"]


def test_sort_by_time_tasks_without_time_go_last():
    """Tasks with no time value should sort after all timed tasks."""
    scheduler = Scheduler()
    tasks = [
        make_task("t2", "No-time task", time=None),
        make_task("t1", "Morning Feed", time="08:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].time == "08:00"
    assert result[1].time is None


def test_sort_by_time_identical_times_preserves_input_order():
    """Two tasks at the same time should not raise and should maintain stable order."""
    scheduler = Scheduler()
    tasks = [
        make_task("t1", "Task A", time="09:00"),
        make_task("t2", "Task B", time="09:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert len(result) == 2
    assert result[0].task_id == "t1"
    assert result[1].task_id == "t2"


# ---------------------------------------------------------------------------
# Recurrence logic — completing a daily task creates a next-day task
# ---------------------------------------------------------------------------

def test_mark_task_complete_creates_next_day_task_for_daily():
    scheduler = Scheduler()
    pet = make_pet()
    task = make_task("feed-1", "Morning Feed", recurrence="daily")
    pet.tasks.append(task)

    next_task = scheduler.mark_task_complete(task, pet)

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date_or_day == date.today() + timedelta(days=1)
    assert next_task.task_id == "feed-1_next"
    assert len(pet.tasks) == 2  # original + new occurrence


def test_mark_task_complete_original_is_marked_done():
    scheduler = Scheduler()
    pet = make_pet()
    task = make_task("feed-1", "Morning Feed", recurrence="daily")
    pet.tasks.append(task)

    scheduler.mark_task_complete(task, pet)

    assert task.completed is True


def test_mark_task_complete_returns_none_for_one_off_task():
    scheduler = Scheduler()
    pet = make_pet()
    task = make_task("vet-1", "Vet Visit", recurrence="once")
    pet.tasks.append(task)

    next_task = scheduler.mark_task_complete(task, pet)

    assert next_task is None
    assert len(pet.tasks) == 1  # no new task appended


# ---------------------------------------------------------------------------
# Conflict detection — same time slot is flagged
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_duplicate_time_slots():
    scheduler = Scheduler()
    tasks = [
        make_task("t1", "Morning Walk", time="08:00", pet_name="Buddy"),
        make_task("t2", "Morning Feed", time="08:00", pet_name="Buddy"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_no_warnings_for_different_times():
    scheduler = Scheduler()
    tasks = [
        make_task("t1", "Morning Walk", time="08:00"),
        make_task("t2", "Afternoon Feed", time="13:00"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert warnings == []


def test_detect_conflicts_skips_completed_tasks():
    """A completed task should not count as occupying its time slot."""
    scheduler = Scheduler()
    done = make_task("t1", "Done Task", time="08:00")
    done.mark_complete()
    pending = make_task("t2", "Pending Task", time="08:00")

    warnings = scheduler.detect_conflicts([done, pending])
    assert warnings == []


def test_detect_conflicts_skips_tasks_without_time():
    """Tasks with no time set have no defined slot and should never conflict."""
    scheduler = Scheduler()
    tasks = [
        make_task("t1", "Unscheduled A", time=None),
        make_task("t2", "Unscheduled B", time=None),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert warnings == []


def test_detect_conflicts_three_tasks_same_slot_produces_three_warnings():
    """3 tasks at the same time → C(3,2) = 3 pairwise warnings."""
    scheduler = Scheduler()
    tasks = [
        make_task("t1", "Task A", time="10:00"),
        make_task("t2", "Task B", time="10:00"),
        make_task("t3", "Task C", time="10:00"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 3
