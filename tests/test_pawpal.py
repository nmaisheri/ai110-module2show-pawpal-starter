from pawpal_system import Pet, Task


def make_task(task_id="t1", title="Test Task", duration=15, priority="medium"):
    return Task(
        task_id=task_id,
        title=title,
        category="exercise",
        duration_minutes=duration,
        priority=priority,
        recurrence="daily",
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    assert len(pet.tasks) == 0
    pet.tasks.append(make_task("t1", "Morning Walk"))
    pet.tasks.append(make_task("t2", "Feeding"))
    assert len(pet.tasks) == 2
