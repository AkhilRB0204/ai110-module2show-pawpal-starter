"""PawPal+ logic layer: the backend classes behind the Streamlit app.

Class skeletons generated from diagrams/uml.mmd. Method bodies are stubs
and will be filled in as the scheduling logic is implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration: int  # minutes
    priority: str = "medium"  # "low", "medium", or "high"
    frequency: str = "daily"  # "daily" or "weekly"
    preferred_time: str | None = None  # e.g. "08:00"
    completed: bool = False

    def priority_rank(self) -> int:
        """Return a number for sorting: high=3, medium=2, low=1."""
        pass

    def is_due_today(self, day: date) -> bool:
        """Return True if this task should be scheduled on the given day."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, task_title: str) -> None:
        """Remove the task with the given title."""
        pass

    def edit_task(self, task_title: str, changes: dict) -> None:
        """Update fields on the task with the given title."""
        pass


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Builds a daily care plan for an owner's pets within their time budget."""

    def __init__(self, owner: Owner, day_start: str = "08:00") -> None:
        self.owner = owner
        self.day_start = day_start
        self.plan: list = []  # scheduled entries: (start_time, task, reason)
        self.skipped: list = []  # tasks left out: (task, reason)

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (highest first), then by duration."""
        pass

    def filter_tasks(self, tasks: list[Task]) -> list[Task]:
        """Keep only the tasks that fit in the owner's available time."""
        pass

    def detect_conflicts(self) -> list:
        """Find tasks in the plan whose time slots overlap."""
        pass

    def generate_plan(self) -> list:
        """Build today's plan from the owner's tasks and return it."""
        pass

    def explain_plan(self) -> str:
        """Describe in plain English why the plan looks the way it does."""
        pass
