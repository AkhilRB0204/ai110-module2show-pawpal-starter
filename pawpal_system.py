"""PawPal+ logic layer: the backend classes behind the Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from itertools import combinations

PRIORITY_RANKS = {"high": 3, "medium": 2, "low": 1}
REPEAT_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def to_minutes(hhmm: str) -> int:
    """Convert a "HH:MM" string to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight to a "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration: int  # minutes
    priority: str = "medium"  # "low", "medium", or "high"
    frequency: str = "daily"  # "daily", "weekly", or "once"
    preferred_time: str | None = None  # e.g. "08:00"
    completed: bool = False
    due_date: date | None = None  # None means due whenever it is next planned
    pet_name: str = ""  # set when the task is added to a pet

    def priority_rank(self) -> int:
        """Return a number for sorting: high=3, medium=2, low=1."""
        return PRIORITY_RANKS.get(self.priority, 0)

    def is_due_today(self, day: date) -> bool:
        """Return True if this task is not done yet and is due on or before the given day."""
        return not self.completed and (self.due_date is None or self.due_date <= day)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self, day: date) -> Task | None:
        """Return a fresh copy of this task due on its next date, or None if it doesn't repeat."""
        interval = REPEAT_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        return replace(self, completed=False, due_date=day + interval)


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove the task with the given title."""
        self.tasks = [t for t in self.tasks if t.title != task_title]

    def edit_task(self, task_title: str, changes: dict) -> None:
        """Update fields on the task with the given title."""
        for task in self.tasks:
            if task.title == task_title:
                for key, value in changes.items():
                    if not hasattr(task, key):
                        raise AttributeError(f"Task has no field '{key}'")
                    setattr(task, key, value)
                return
        raise ValueError(f"{self.name} has no task named '{task_title}'")


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_pet(self, pet_name: str) -> Pet | None:
        """Return the pet with the given name, or None if there isn't one."""
        return next((p for p in self.pets if p.name == pet_name), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily care plan for an owner's pets within their time budget."""

    def __init__(self, owner: Owner, day_start: str = "08:00") -> None:
        """Create a scheduler for an owner, starting the day at day_start."""
        self.owner = owner
        self.day_start = day_start
        self.plan: list[tuple[str, Task, str]] = []  # (start_time, task, reason)
        self.skipped: list[tuple[Task, str]] = []  # (task, reason)

    # --- Sorting and filtering ---------------------------------------------

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (highest first), then by shortest duration."""
        return sorted(tasks, key=lambda t: (-t.priority_rank(), t.duration))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by preferred time, earliest first; tasks with no time go last."""
        return sorted(
            tasks,
            key=lambda t: to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
        )

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return the owner's tasks, optionally limited to one pet and/or a completion status."""
        return [
            t
            for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def fit_to_time(self, tasks: list[Task]) -> list[Task]:
        """Keep the tasks that fit in the owner's available time, in the given order."""
        kept = []
        minutes_left = self.owner.available_minutes
        for task in tasks:
            if task.duration <= minutes_left:
                kept.append(task)
                minutes_left -= task.duration
            else:
                self.skipped.append(
                    (task, f"needs {task.duration} min, only {minutes_left} min left")
                )
        return kept

    # --- Recurring tasks ---------------------------------------------------

    def mark_task_complete(self, task: Task, day: date | None = None) -> Task | None:
        """Complete a task and, if it repeats, add its next occurrence to the same pet."""
        day = day or date.today()
        task.mark_complete()
        next_task = task.next_occurrence(day)
        pet = self.owner.get_pet(task.pet_name)
        if next_task and pet:
            pet.add_task(next_task)
        return next_task

    # --- Conflict detection ------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each pair of planned tasks whose times overlap."""
        warnings = []
        for (start_a, task_a, _), (start_b, task_b, _) in combinations(self.plan, 2):
            a0, b0 = to_minutes(start_a), to_minutes(start_b)
            if a0 < b0 + task_b.duration and b0 < a0 + task_a.duration:
                who = (
                    f"both for {task_a.pet_name}"
                    if task_a.pet_name == task_b.pet_name
                    else f"{task_a.pet_name} and {task_b.pet_name}"
                )
                warnings.append(
                    f"{task_a.title} at {start_a} overlaps {task_b.title} "
                    f"at {start_b} ({who})"
                )
        return warnings

    # --- Planning ----------------------------------------------------------

    def generate_plan(self, day: date | None = None) -> list[tuple[str, Task, str]]:
        """Build the plan for a day from all of the owner's pets' tasks and return it."""
        day = day or date.today()
        self.plan, self.skipped = [], []

        due = [t for t in self.owner.get_all_tasks() if t.is_due_today(day)]
        chosen = self.fit_to_time(self.sort_by_priority(due))

        # Tasks with a preferred time go there; the rest fill the open gaps
        # from the start of the day, highest priority first.
        busy = []
        for task in chosen:
            if task.preferred_time:
                start = to_minutes(task.preferred_time)
                busy.append((start, start + task.duration))
                self.plan.append(
                    (task.preferred_time, task, f"{task.priority} priority, preferred time")
                )

        cursor = to_minutes(self.day_start)
        for task in chosen:
            if task.preferred_time:
                continue
            moved = True
            while moved:
                moved = False
                for b_start, b_end in busy:
                    if cursor < b_end and b_start < cursor + task.duration:
                        cursor, moved = b_end, True
            busy.append((cursor, cursor + task.duration))
            self.plan.append((to_hhmm(cursor), task, f"{task.priority} priority"))
            cursor += task.duration

        self.plan.sort(key=lambda entry: to_minutes(entry[0]))
        return self.plan

    def explain_plan(self) -> str:
        """Describe in plain English why the plan looks the way it does."""
        used = sum(task.duration for _, task, _ in self.plan)
        lines = [
            f"Scheduled {len(self.plan)} task(s) using {used} of "
            f"{self.owner.available_minutes} available minutes.",
            "Tasks were chosen by priority (high first, then shorter tasks), "
            "placed at their preferred time if they had one, "
            f"and otherwise fit into open slots starting at {self.day_start}.",
        ]
        for task, reason in self.skipped:
            lines.append(f"Skipped {task.title} ({task.pet_name}): {reason}.")
        for warning in self.detect_conflicts():
            lines.append(f"Warning: {warning}.")
        return "\n".join(lines)
