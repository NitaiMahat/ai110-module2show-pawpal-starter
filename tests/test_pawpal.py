from pawpal_system import Task, Pet


def test_mark_done_changes_status():
    task = Task(task_id="t1", pet_name="Buddy", task_type="walk", duration_minutes=30, priority=1)
    assert task.status == "pending"
    task.mark_done()
    assert task.status == "done"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    task = Task(task_id="t1", pet_name="Buddy", task_type="walk", duration_minutes=30, priority=1)
    pet.add_task(task)
    assert len(pet.tasks) == 1
