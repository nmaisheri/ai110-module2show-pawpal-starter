from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
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

    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        raise NotImplementedError

    def set_time_available(self, minutes: int) -> None:
        raise NotImplementedError

    def is_time_window_preferred(self, window: str) -> bool:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    health_notes: str = ""
    energy_level: str = "medium"

    def update_profile(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_care_needs_summary(self) -> str:
        raise NotImplementedError

    def requires_special_handling(self, task_type: str) -> bool:
        raise NotImplementedError


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    due_date_or_day: Optional[date] = None
    recurrence: str = "once"
    preferred_time_window: Optional[str] = None
    mandatory: bool = False
    notes: str = ""

    def is_due_on(self, target_date: date) -> bool:
        raise NotImplementedError

    def is_recurring(self) -> bool:
        raise NotImplementedError

    def priority_score(self) -> int:
        raise NotImplementedError

    def conflicts_with(self, other_task: "Task", start_time: datetime) -> bool:
        raise NotImplementedError


class TaskManager:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def edit_task(self, task_id: int, updates: Dict[str, Any]) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: int) -> None:
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
    scheduled_items: List[str] = field(default_factory=list)
    unscheduled_tasks: List[str] = field(default_factory=list)
    total_minutes_scheduled: int = 0
    explanation_log: List[str] = field(default_factory=list)

    def add_scheduled_task(self, task: Task, start_time: datetime) -> None:
        raise NotImplementedError

    def add_unscheduled_task(self, task: Task, reason: str) -> None:
        raise NotImplementedError

    def total_time(self) -> int:
        raise NotImplementedError

    def to_display_format(self) -> str:
        raise NotImplementedError

    def explain_choices(self) -> str:
        raise NotImplementedError


class Scheduler:
    def __init__(self, strategy: str = "priority_first", constraints: Optional[Dict[str, Any]] = None) -> None:
        self.strategy = strategy
        self.constraints = constraints or {}

    def generate_plan(self, tasks: List[Task], owner: Owner, pet: Pet, target_date: date) -> DailyPlan:
        raise NotImplementedError

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        raise NotImplementedError

    def select_tasks_within_time_limit(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        raise NotImplementedError

    def place_tasks_on_timeline(self, tasks: List[Task], windows: List[str]) -> None:
        raise NotImplementedError

    def resolve_conflicts(self, plan: DailyPlan) -> None:
        raise NotImplementedError

    def build_reasoning(self, plan: DailyPlan) -> None:
        raise NotImplementedError
