from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


class Owner:
    def __init__(
        self,
        name: str,
        daily_time_available_minutes: int,
        preferred_time_windows: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.daily_time_available_minutes = daily_time_available_minutes
        self.preferred_time_windows = preferred_time_windows or []
        self.preferences = preferences or {}
        self.pets: List[Pet] = []

    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        """Merge new key-value pairs into the owner's preferences dict."""
        self.preferences.update(new_preferences)

    def set_time_available(self, minutes: int) -> None:
        """Update the number of minutes the owner has available each day."""
        self.daily_time_available_minutes = minutes

    def is_time_window_preferred(self, window: str) -> bool:
        """Return True if the given time window is in the owner's preferred list."""
        return window in self.preferred_time_windows

    def add_pet(self, pet: "Pet") -> None:
        """Append a pet to the owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from the owner's list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_pets(self) -> List["Pet"]:
        """Return all pets belonging to this owner."""
        return self.pets

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Persist the owner, their preferences, and all pets/tasks to a JSON file."""
        payload = {
            "name": self.name,
            "daily_time_available_minutes": self.daily_time_available_minutes,
            "preferred_time_windows": self.preferred_time_windows,
            "preferences": self.preferences,
            "pets": [p.to_dict() for p in self.pets],
        }
        with open(filepath, "w") as f:
            json.dump(payload, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load an Owner (with all pets and tasks) from a JSON file.

        Returns None if the file does not exist so callers can treat a missing
        file as a first-run condition without raising an exception.
        """
        if not os.path.exists(filepath):
            return None
        with open(filepath) as f:
            data = json.load(f)
        owner = cls(
            name=data["name"],
            daily_time_available_minutes=data["daily_time_available_minutes"],
            preferred_time_windows=data.get("preferred_time_windows", []),
            preferences=data.get("preferences", {}),
        )
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return owner


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    health_notes: str = ""
    energy_level: str = "medium"
    tasks: List["Task"] = field(default_factory=list)

    def update_profile(self, data: Dict[str, Any]) -> None:
        """Update any pet attribute that exists on this dataclass from a dict."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_care_needs_summary(self) -> str:
        """Return a one-line string summarising the pet's species, breed, age, and energy."""
        return (
            f"{self.name} ({self.species}, {self.breed}, age {self.age}) — "
            f"energy: {self.energy_level}"
            + (f", notes: {self.health_notes}" if self.health_notes else "")
        )

    def requires_special_handling(self, task_type: str) -> bool:
        """Return True for medical tasks or any pet that has health notes recorded."""
        return task_type.lower() == "medical" or bool(self.health_notes)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this Pet (and its tasks) to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "health_notes": self.health_notes,
            "energy_level": self.energy_level,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """Reconstruct a Pet (and its tasks) from a dictionary produced by to_dict()."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data["breed"],
            age=data["age"],
            health_notes=data.get("health_notes", ""),
            energy_level=data.get("energy_level", "medium"),
        )
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


@dataclass
class Task:
    task_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    pet_name: Optional[str] = None
    due_date_or_day: Optional[date] = None
    recurrence: str = "once"
    preferred_time_window: Optional[str] = None
    mandatory: bool = False
    notes: str = ""
    completed: bool = False
    time: Optional[str] = None  # "HH:MM" format, e.g. "08:30"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due_on(self, target_date: date) -> bool:
        """Return True if this task should appear in the schedule for target_date."""
        if self.recurrence == "daily":
            return True
        if self.recurrence == "weekly" and self.due_date_or_day:
            return target_date.weekday() == self.due_date_or_day.weekday()
        if self.recurrence == "once" and self.due_date_or_day:
            return self.due_date_or_day == target_date
        return False

    def is_recurring(self) -> bool:
        """Return True if the task repeats (daily or weekly)."""
        return self.recurrence in ("daily", "weekly")

    def priority_score(self) -> int:
        """Return a numeric score (1–5) used to rank this task; mandatory tasks score higher."""
        scores = {"high": 3, "medium": 2, "low": 1}
        base = scores.get(self.priority.lower(), 1)
        return base + (2 if self.mandatory else 0)

    def conflicts_with(self, other_task: "Task", start_time: datetime) -> bool:
        """Return True if this task's time window overlaps other_task when both start at start_time."""
        from datetime import timedelta
        my_end = start_time + timedelta(minutes=self.duration_minutes)
        other_end = start_time + timedelta(minutes=other_task.duration_minutes)
        return start_time < other_end and my_end > start_time

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this Task to a JSON-safe dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "pet_name": self.pet_name,
            "due_date_or_day": self.due_date_or_day.isoformat() if self.due_date_or_day else None,
            "recurrence": self.recurrence,
            "preferred_time_window": self.preferred_time_window,
            "mandatory": self.mandatory,
            "notes": self.notes,
            "completed": self.completed,
            "time": self.time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Reconstruct a Task from a dictionary produced by to_dict()."""
        raw_date = data.get("due_date_or_day")
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            category=data["category"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            pet_name=data.get("pet_name"),
            due_date_or_day=date.fromisoformat(raw_date) if raw_date else None,
            recurrence=data.get("recurrence", "once"),
            preferred_time_window=data.get("preferred_time_window"),
            mandatory=data.get("mandatory", False),
            notes=data.get("notes", ""),
            completed=data.get("completed", False),
            time=data.get("time"),
        )


class TaskManager:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def edit_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks_for_day(self, target_date: date) -> List[Task]:
        raise NotImplementedError

    def filter_tasks(self, criteria: Dict[str, Any]) -> List[Task]:
        raise NotImplementedError

    def sort_tasks(self, by_priority: bool = True, by_duration: bool = False) -> List[Task]:
        raise NotImplementedError


@dataclass
class DailyPlan:
    date: date
    owner: Owner
    pet: Pet
    scheduled_items: List[Dict[str, Any]] = field(default_factory=list)
    unscheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    total_minutes_scheduled: int = 0
    explanation_log: List[str] = field(default_factory=list)

    def add_scheduled_task(self, task: Task, start_time: datetime) -> None:
        """Append a task to the scheduled list and increment the total time counter."""
        self.scheduled_items.append({"task": task, "start_time": start_time})
        self.total_minutes_scheduled += task.duration_minutes

    def add_unscheduled_task(self, task: Task, reason: str) -> None:
        """Record a task that could not be scheduled along with the reason it was skipped."""
        self.unscheduled_tasks.append({"task": task, "reason": reason})

    def total_time(self) -> int:
        """Return the total minutes consumed by all scheduled tasks."""
        return self.total_minutes_scheduled

    def to_display_format(self) -> str:
        """Return a human-readable, line-by-line summary of the day's plan."""
        lines = [f"Daily Plan for {self.pet.name} on {self.date} (owner: {self.owner.name})"]
        for item in self.scheduled_items:
            t = item["task"]
            lines.append(f"  {item['start_time'].strftime('%H:%M')} — {t.title} ({t.duration_minutes} min)")
        if self.unscheduled_tasks:
            lines.append("  [Not scheduled]")
            for item in self.unscheduled_tasks:
                lines.append(f"    - {item['task'].title}: {item['reason']}")
        return "\n".join(lines)

    def explain_choices(self) -> str:
        """Return the explanation log as a single newline-joined string."""
        return "\n".join(self.explanation_log)


class Scheduler:
    def __init__(self, strategy: str = "priority_first", constraints: Optional[Dict[str, Any]] = None) -> None:
        self.strategy = strategy
        self.constraints = constraints or {}

    def get_all_tasks(self, owner: Owner) -> List[Task]:
        """Collect every task across all of the owner's pets."""
        all_tasks: List[Task] = []
        for pet in owner.get_pets():
            all_tasks.extend(pet.tasks)
        return all_tasks

    def generate_plan(self, tasks: List[Task], owner: Owner, pet: Pet, target_date: date) -> DailyPlan:
        """Build and return a DailyPlan by filtering, ranking, and placing due tasks."""
        due_tasks = [t for t in tasks if t.is_due_on(target_date)]
        ranked = self.rank_tasks(due_tasks)
        selected = self.select_tasks_within_time_limit(ranked, owner.daily_time_available_minutes)

        plan = DailyPlan(date=target_date, owner=owner, pet=pet)
        from datetime import datetime, timedelta
        cursor = datetime(target_date.year, target_date.month, target_date.day, 8, 0)
        for task in selected:
            plan.add_scheduled_task(task, cursor)
            cursor += timedelta(minutes=task.duration_minutes)

        for task in ranked:
            if task not in selected:
                plan.add_unscheduled_task(task, "insufficient time remaining")

        self.build_reasoning(plan)
        return plan

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted descending by priority_score so highest-priority tasks go first."""
        return sorted(tasks, key=lambda t: t.priority_score(), reverse=True)

    def select_tasks_within_time_limit(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Greedily pick tasks in ranked order until the available time budget is exhausted."""
        selected: List[Task] = []
        remaining = available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def place_tasks_on_timeline(self, tasks: List[Task], windows: List[str]) -> None:
        """Assign each task a preferred_time_window by cycling through the provided windows."""
        for i, task in enumerate(tasks):
            if windows:
                task.preferred_time_window = windows[i % len(windows)]

    def resolve_conflicts(self, plan: DailyPlan) -> None:
        """Remove duplicate task entries from the plan, keeping the first occurrence."""
        seen_ids: set = set()
        deduped = []
        for item in plan.scheduled_items:
            tid = item["task"].task_id
            if tid not in seen_ids:
                seen_ids.add(tid)
                deduped.append(item)
        plan.scheduled_items = deduped

    def mark_task_complete(self, task: Task, pet: "Pet") -> Optional[Task]:
        """Mark task complete and, for daily/weekly tasks, append a new instance to the pet.

        Returns the newly created Task, or None for one-off tasks.
        """
        task.mark_complete()

        intervals = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        if task.recurrence not in intervals:
            return None

        next_task = replace(
            task,
            task_id=f"{task.task_id}_next",
            due_date_or_day=date.today() + intervals[task.recurrence],
            completed=False,
        )
        pet.tasks.append(next_task)
        return next_task

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted chronologically by their 'time' attribute (HH:MM string).

        Uses a lambda key so Python's sorted() can compare time strings lexicographically —
        valid because "HH:MM" zero-padded strings sort in the same order as actual clock times.
        Tasks that have no time value are assigned the sentinel "99:99" so they always sort last
        rather than raising an error or being silently dropped.
        """
        return sorted(tasks, key=lambda t: t.time if t.time is not None else "99:99")

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return a list of warning strings for any two pending tasks that share the same time slot.

        Uses a lightweight O(n²) pairwise check on the 'time' field — no crash, just warnings.
        Completed tasks are excluded since they no longer occupy a slot in the active schedule.
        Tasks without a time value are skipped since they have no defined slot to conflict with.
        """
        warnings: List[str] = []
        timed = [t for t in tasks if t.time is not None and not t.completed]
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                if a.time == b.time:
                    warnings.append(
                        f"WARNING: '{a.title}' ({a.pet_name or 'unknown'}) and "
                        f"'{b.title}' ({b.pet_name or 'unknown'}) are both scheduled at {a.time}."
                    )
        return warnings

    def filter_tasks(self, tasks: List[Task], completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return the subset of tasks that match all provided filters.

        Both parameters are optional and composable — omitting one means "don't filter on that axis."
        - completed=True  → only tasks already marked done
        - completed=False → only pending tasks
        - pet_name="Buddy" → only tasks belonging to that pet (exact match on Task.pet_name)
        Passing both narrows to tasks that satisfy both conditions simultaneously.
        """
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        return result

    def build_reasoning(self, plan: DailyPlan) -> None:
        """Populate the plan's explanation_log with a sentence for each scheduled and skipped task."""
        for item in plan.scheduled_items:
            task = item["task"]
            plan.explanation_log.append(
                f"Scheduled '{task.title}' (priority={task.priority}, "
                f"{task.duration_minutes} min) at {item['start_time'].strftime('%H:%M')}"
            )
        for item in plan.unscheduled_tasks:
            plan.explanation_log.append(
                f"Skipped '{item['task'].title}': {item['reason']}"
            )
