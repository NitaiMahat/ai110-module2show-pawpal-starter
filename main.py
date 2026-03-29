from datetime import datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler


def format_schedule(tasks):
    lines = ["Today's Schedule:"]
    for task in tasks:
        preferred = task.preferred_time.strftime('%H:%M') if task.preferred_time else 'Anytime'
        lines.append(
            f"- [{task.status}] {task.pet_name}: {task.task_type} (priority {task.priority}, duration {task.duration_minutes} min, at {preferred})"
        )
    return "\n".join(lines)


def main():
    owner = Owner(name='Alex', contact_info='alex@example.com')
    owner.set_availability(['08:00-10:00', '17:00-20:00'])

    pet1 = Pet(name='Buddy', species='Dog', breed='Labrador', age=5)
    pet2 = Pet(name='Mittens', species='Cat', age=3)

    task1 = Task(task_id='t1', pet_name='Buddy', task_type='Walk', duration_minutes=30, priority=5, preferred_time=time(8, 30))
    task2 = Task(task_id='t2', pet_name='Buddy', task_type='Feed', duration_minutes=10, priority=10, preferred_time=time(7, 30))
    task3 = Task(task_id='t3', pet_name='Mittens', task_type='Med', duration_minutes=5, priority=8, preferred_time=time(9, 0))

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(date=datetime.now())
    plan = scheduler.generate_plan(owner)

    print(format_schedule(plan))
    print(f"Plan score: {scheduler.score_task_order():.2f}")
    print(f"Conflict flagged: {scheduler.conflict_check()}")


if __name__ == '__main__':
    main()
