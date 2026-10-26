from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Mochi"


def test_scheduler_plans_tasks_from_every_pet():
    owner = Owner("Jordan", available_minutes=60)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    dog.add_task(Task("Walk", 20, "high"))
    cat.add_task(Task("Feed", 5, "high"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    plan = Scheduler(owner).generate_plan(date(2026, 10, 25))

    assert {task.pet_name for _, task, _ in plan} == {"Mochi", "Luna"}


def test_scheduler_skips_tasks_that_do_not_fit():
    owner = Owner("Jordan", available_minutes=30)
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 25, "high"))
    pet.add_task(Task("Bath", 45, "low"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(date(2026, 10, 25))

    assert [task.title for _, task, _ in plan] == ["Walk"]
    assert [task.title for task, _ in scheduler.skipped] == ["Bath"]
