from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 10, 25)


def make_owner(minutes=120):
    owner = Owner("Jordan", available_minutes=minutes)
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Luna", "cat"))
    return owner


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
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 20, "high"))
    owner.pets[1].add_task(Task("Feed", 5, "high"))

    plan = Scheduler(owner).generate_plan(TODAY)

    assert {task.pet_name for _, task, _ in plan} == {"Mochi", "Luna"}


def test_scheduler_skips_tasks_that_do_not_fit():
    owner = make_owner(minutes=30)
    owner.pets[0].add_task(Task("Walk", 25, "high"))
    owner.pets[0].add_task(Task("Bath", 45, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(TODAY)

    assert [task.title for _, task, _ in plan] == ["Walk"]
    assert [task.title for task, _ in scheduler.skipped] == ["Bath"]


def test_sort_by_time_orders_by_clock_and_puts_untimed_last():
    owner = make_owner()
    pet = owner.pets[0]
    pet.add_task(Task("Dinner", 10, preferred_time="18:00"))
    pet.add_task(Task("Play", 10))
    pet.add_task(Task("Walk", 10, preferred_time="07:30"))
    pet.add_task(Task("Pill", 5, preferred_time="9:15"))  # no leading zero

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Walk", "Pill", "Dinner", "Play"]


def test_filter_tasks_by_pet_and_status():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 20))
    owner.pets[1].add_task(Task("Feed", 5))
    owner.pets[1].add_task(Task("Brush", 10, completed=True))
    scheduler = Scheduler(owner)

    assert [t.title for t in scheduler.filter_tasks(pet_name="Luna")] == ["Feed", "Brush"]
    assert [t.title for t in scheduler.filter_tasks(completed=True)] == ["Brush"]
    assert [
        t.title for t in scheduler.filter_tasks(pet_name="Luna", completed=False)
    ] == ["Feed"]


def test_completing_daily_task_creates_tomorrows_copy():
    owner = make_owner()
    walk = Task("Walk", 20, frequency="daily")
    owner.pets[0].add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(walk, TODAY)

    assert walk.completed is True
    assert next_walk.due_date == date(2026, 10, 26)
    assert next_walk.completed is False
    assert next_walk in owner.pets[0].tasks
    assert not next_walk.is_due_today(TODAY)


def test_completing_weekly_task_is_due_in_seven_days():
    owner = make_owner()
    bath = Task("Bath", 45, frequency="weekly")
    owner.pets[0].add_task(bath)

    next_bath = Scheduler(owner).mark_task_complete(bath, TODAY)

    assert next_bath.due_date == date(2026, 11, 1)


def test_one_time_task_does_not_repeat():
    owner = make_owner()
    vet = Task("Vet visit", 60, frequency="once")
    owner.pets[0].add_task(vet)

    assert Scheduler(owner).mark_task_complete(vet, TODAY) is None
    assert len(owner.pets[0].tasks) == 1


def test_detect_conflicts_warns_about_same_time_tasks():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, "high", preferred_time="07:30"))
    owner.pets[1].add_task(Task("Pill", 5, "high", preferred_time="07:30"))
    scheduler = Scheduler(owner)

    scheduler.generate_plan(TODAY)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Pill" in warnings[0]


def test_no_conflicts_when_tasks_do_not_overlap():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, preferred_time="07:00"))
    owner.pets[1].add_task(Task("Pill", 5, preferred_time="07:30"))
    scheduler = Scheduler(owner)

    scheduler.generate_plan(TODAY)

    assert scheduler.detect_conflicts() == []
