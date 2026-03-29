from dataclasses import dataclass, field
from datetime import datetime, time, date, timedelta
from typing import List, Optional, Dict


@dataclass
class Task:
    task_id: str
    pet_name: str
    task_type: str
    duration_minutes: int
    priority: int
    preferred_time: Optional[time] = None
    status: str = "pending"
    frequency: str = "once"          # "once" | "daily" | "weekly"
    due_date: Optional[date] = None  # the calendar date this task is due

    def mark_done(self) -> None:
        """Mark this task as completed by setting its status to 'done'."""
        self.status = "done"

    def next_occurrence(self, counter: int) -> Optional["Task"]:
        """Return a new Task for the next occurrence if this task is recurring, else None.

        Uses timedelta to advance due_date by 1 day (daily) or 7 days (weekly).
        The caller is responsible for adding the returned task to the appropriate pet.
        """
        if self.frequency == "once":
            return None
        delta = timedelta(days=1 if self.frequency == "daily" else 7)
        next_due = (self.due_date + delta) if self.due_date else (date.today() + delta)
        return Task(
            task_id=f"{self.task_id}_r{counter}",
            pet_name=self.pet_name,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            status="pending",
            frequency=self.frequency,
            due_date=next_due,
        )

    def reschedule(self, new_time: time) -> None:
        """Update the preferred time for this task."""
        self.preferred_time = new_time

    def update_details(self, **kwargs) -> None:
        """Update any task field by keyword argument if the attribute exists."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    health_notes: Optional[str] = None
    care_requirements: Dict[str, str] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)

    def update_health_notes(self, notes: str) -> None:
        """Replace the pet's health notes with new text."""
        self.health_notes = notes

    def describe(self) -> str:
        """Return a human-readable summary string for this pet."""
        return f"{self.name} ({self.species}, breed={self.breed}, age={self.age})"

    def needs_task(self, task_type: str) -> bool:
        """Return True if the pet has an incomplete task of the given type."""
        return any(task.task_type == task_type and task.status != "done" for task in self.tasks)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    contact_info: str
    preferences: Dict[str, str] = field(default_factory=dict)
    available_time_slots: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def update_preferences(self, new_preferences: Dict[str, str]) -> None:
        """Merge new key-value pairs into the owner's preferences."""
        self.preferences.update(new_preferences)

    def set_availability(self, slots: List[str]) -> None:
        """Replace the owner's available time slots with the provided list."""
        self.available_time_slots = slots

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pet list."""
        self.pets.append(pet)

    def get_summary(self) -> Dict[str, str]:
        """Return a dictionary summarising the owner's pets, preferences, and availability."""
        return {
            "owner": self.name,
            "pets": ", ".join([pet.name for pet in self.pets]),
            "preferences": str(self.preferences),
            "availability": ", ".join(self.available_time_slots),
        }

    def get_all_tasks(self) -> List[Task]:
        """Collect and return every task across all of the owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    def __init__(self, date: datetime):
        self.date = date
        self.assigned_tasks: List[Task] = []
        self.constraints: Dict[str, str] = {}
        self.plan_description: Optional[str] = None
        self._recur_counter: int = 0  # used to generate unique IDs for recurring tasks

    def generate_plan(self, owner: Owner) -> List[Task]:
        """Build and return a prioritised task plan for the owner's pending tasks."""
        tasks = [task for task in owner.get_all_tasks() if task.status != "done"]

        # Sort by priority (desc), then by preferred_time (as available)
        tasks.sort(key=lambda t: (-t.priority, t.preferred_time or time(23, 59)))

        self.assigned_tasks = tasks
        self.plan_description = f"Generated plan for {self.date.date()} with {len(tasks)} tasks."
        return self.assigned_tasks

    # ── Step 2: Sorting ───────────────────────────────────────────────────────

    def sort_by_time(self) -> List[Task]:
        """Return assigned tasks sorted ascending by preferred_time.

        Tasks without a preferred_time are placed at the end (treated as 23:59).
        Uses sorted() with a lambda key so the original list order is preserved
        as a stable tiebreaker.
        """
        return sorted(
            self.assigned_tasks,
            key=lambda t: t.preferred_time or time(23, 59),
        )

    # ── Step 2: Filtering ─────────────────────────────────────────────────────

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Task]:
        """Return a filtered subset of assigned tasks.

        Pass pet_name to keep only that pet's tasks.
        Pass status (e.g. 'pending', 'done') to keep only tasks in that state.
        Both filters can be combined; omitting a parameter skips that filter.
        """
        result = self.assigned_tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if status is not None:
            result = [t for t in result if t.status == status]
        return result

    # ── Step 3: Recurring task completion ────────────────────────────────────

    def mark_task_complete(self, task_id: str, owner: Owner) -> Optional[Task]:
        """Mark a task done and, if it is recurring, spawn the next occurrence.

        Finds the task by ID in assigned_tasks, calls mark_done(), then calls
        next_occurrence() to build the follow-up task.  The new task is added
        to the matching pet via pet.add_task() so it persists in the owner's
        data for the next generate_plan() call.

        Returns the newly created Task if one was spawned, otherwise None.
        """
        target = next((t for t in self.assigned_tasks if t.task_id == task_id), None)
        if target is None:
            return None

        target.mark_done()
        self._recur_counter += 1
        new_task = target.next_occurrence(self._recur_counter)

        if new_task is not None:
            for pet in owner.pets:
                if pet.name == target.pet_name:
                    pet.add_task(new_task)
                    break

        return new_task

    def score_task_order(self) -> float:
        """Return the average priority score of the current assigned task list."""
        if not self.assigned_tasks:
            return 0.0
        total_priority = sum(task.priority for task in self.assigned_tasks)
        return total_priority / len(self.assigned_tasks)

    def conflict_check(self) -> bool:
        """Return True if any two assigned tasks share the same preferred time."""
        times = [task.preferred_time for task in self.assigned_tasks if task.preferred_time is not None]
        return len(times) != len(set(times))

    def get_todays_tasks(self) -> List[Task]:
        """Return the list of tasks assigned for today's schedule."""
        return self.assigned_tasks
