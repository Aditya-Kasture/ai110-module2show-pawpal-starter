"""
PawPal+ backend classes.

Design:
  Owner  ──< Pet  (one owner can have many pets)
  Pet    ──< Task (each pet has its own task list)
  Scheduler uses Owner to build a prioritized daily plan
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single care activity that can be scheduled in a day."""

    title: str
    duration_minutes: int
    priority: str                        # "low" | "medium" | "high"
    time: str = "09:00"                  # "HH:MM" 24-hour
    frequency: str = "once"             # "once" | "daily" | "weekly"
    is_complete: bool = False
    due_date: Optional[date] = None
    pet_name: Optional[str] = None
    notes: str = ""

    def priority_rank(self) -> int:
        """Return numeric rank so tasks can be sorted: high=3, medium=2, low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)

    def is_schedulable(self, available_minutes: int) -> bool:
        """Return True if this task fits in the remaining available time."""
        return self.duration_minutes <= available_minutes

    def mark_complete(self) -> None:
        """Mark task complete; advance due date automatically for recurring tasks."""
        if self.frequency == "daily" and self.due_date:
            self.due_date = self.due_date + timedelta(days=1)
            # recurring — stays incomplete for next occurrence
        elif self.frequency == "weekly" and self.due_date:
            self.due_date = self.due_date + timedelta(weeks=1)
        else:
            self.is_complete = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet being cared for."""

    name: str
    species: str
    age_years: float
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short human-readable description of the pet."""
        needs = f", special needs: {', '.join(self.special_needs)}" if self.special_needs else ""
        return f"{self.name} ({self.species}, {self.age_years}y{needs})"

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Represents the pet owner who manages pets and tasks."""

    def __init__(self, name: str, available_minutes_per_day: int = 120):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care list."""
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a care task directly to the owner's master task list."""
        self.tasks.append(task)

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks assigned to a specific pet or shared tasks."""
        return [t for t in self.tasks if t.pet_name == pet_name or t.pet_name is None]

    def all_tasks(self) -> list[Task]:
        """Return every task across all pets and owner-level tasks (deduped)."""
        pet_tasks = [t for pet in self.pets for t in pet.tasks]
        seen = {id(t) for t in pet_tasks}
        owner_only = [t for t in self.tasks if id(t) not in seen]
        return pet_tasks + owner_only


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds and explains a prioritized daily care schedule."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self._plan: list[Task] = []

    def build_plan(self) -> list[Task]:
        """
        Select tasks that fit within the owner's available time.
        Strategy: sort by priority (high → low), add greedily until time runs out.
        """
        sorted_tasks = sorted(
            self.owner.all_tasks(),
            key=lambda t: t.priority_rank(),
            reverse=True,
        )
        remaining = self.owner.available_minutes_per_day
        plan = []
        for task in sorted_tasks:
            if task.is_schedulable(remaining):
                plan.append(task)
                remaining -= task.duration_minutes
        self._plan = plan
        return self._plan

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted chronologically by their HH:MM time."""
        return sorted(self.owner.all_tasks(), key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return tasks assigned to the given pet."""
        return [t for t in self.owner.all_tasks() if t.pet_name == pet_name]

    def filter_by_status(self, is_complete: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in self.owner.all_tasks() if t.is_complete == is_complete]

    def detect_conflicts(self) -> list[str]:
        """
        Return warning messages for tasks sharing the same time slot.
        Flags exact time matches; does not check overlapping durations.
        """
        tasks = self.owner.all_tasks()
        warnings: list[str] = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time:
                    warnings.append(
                        f"Conflict at {tasks[i].time}: "
                        f"'{tasks[i].title}' and '{tasks[j].title}'"
                    )
        return warnings

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the generated schedule."""
        if not self._plan:
            self.build_plan()
        if not self._plan:
            return "No tasks could be scheduled today."
        lines = [f"Daily plan for {self.owner.name}:", ""]
        for task in sorted(self._plan, key=lambda t: t.time):
            pet_label = f" [{task.pet_name}]" if task.pet_name else ""
            lines.append(
                f"  {task.time}  {task.title}{pet_label}"
                f"  ({task.duration_minutes} min, priority: {task.priority})"
            )
        lines.append(
            f"\nTotal: {self.total_scheduled_minutes()} min"
            f" of {self.owner.available_minutes_per_day} min available"
        )
        return "\n".join(lines)

    def total_scheduled_minutes(self) -> int:
        """Return total minutes of all scheduled tasks in the current plan."""
        return sum(t.duration_minutes for t in self._plan)

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete; handles recurring rescheduling automatically."""
        task.mark_complete()
