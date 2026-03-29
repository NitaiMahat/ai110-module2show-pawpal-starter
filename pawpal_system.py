from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional, Dict


@dataclass
class Owner:
    name: str
    contact_info: str
    preferences: Dict[str, str] = field(default_factory=dict)
    available_time_slots: List[str] = field(default_factory=list)

    def update_preferences(self, new_preferences: Dict[str, str]) -> None:
        pass

    def set_availability(self, slots: List[str]) -> None:
        pass

    def get_summary(self) -> Dict[str, str]:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    health_notes: Optional[str] = None
    care_requirements: Dict[str, str] = field(default_factory=dict)

    def update_health_notes(self, notes: str) -> None:
        pass

    def describe(self) -> str:
        pass

    def needs_task(self, task_type: str) -> bool:
        pass


@dataclass
class Task:
    task_id: str
    pet_name: str
    task_type: str
    duration_minutes: int
    priority: int
    preferred_time: Optional[time] = None
    status: str = "pending"

    def mark_done(self) -> None:
        pass

    def reschedule(self, new_time: time) -> None:
        pass

    def update_details(self, **kwargs) -> None:
        pass


class Scheduler:
    def __init__(self, date: datetime):
        self.date = date
        self.assigned_tasks: List[Task] = []
        self.constraints: Dict[str, str] = {}
        self.plan_description: Optional[str] = None

    def generate_plan(self, tasks: List[Task], owner: Owner, pets: List[Pet]) -> None:
        pass

    def score_task_order(self) -> float:
        pass

    def conflict_check(self) -> bool:
        pass

    def get_todays_tasks(self) -> List[Task]:
        pass
