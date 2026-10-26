from datetime import date

import pytest

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


# --- Edge cases -----------------------------------------------------------


def test_owner_with_no_pets_gets_empty_plan():
    owner = Owner("Jordan", available_minutes=60)
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan(TODAY) == []
    assert scheduler.detect_conflicts() == []


def test_pet_with_no_tasks_is_ignored():
    owner = make_owner()
    owner.pets[1].add_task(Task("Feed", 5))

    plan = Scheduler(owner).generate_plan(TODAY)

    assert [task.title for _, task, _ in plan] == ["Feed"]


def test_sort_by_time_keeps_same_time_tasks_in_added_order():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, preferred_time="07:30"))
    owner.pets[1].add_task(Task("Pill", 5, preferred_time="07:30"))
    owner.pets[0].add_task(Task("Breakfast", 10, preferred_time="07:00"))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Breakfast", "Walk", "Pill"]


def test_new_daily_copy_is_due_tomorrow_and_keeps_its_details():
    owner = make_owner()
    walk = Task("Walk", 20, "high", preferred_time="07:30")
    owner.pets[0].add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(walk, TODAY)

    assert next_walk is not walk
    assert next_walk.is_due_today(date(2026, 10, 26))
    assert (next_walk.title, next_walk.priority, next_walk.preferred_time, next_walk.pet_name) == (
        "Walk",
        "high",
        "07:30",
        "Mochi",
    )


def test_completing_same_task_twice_does_not_duplicate_it():
    owner = make_owner()
    walk = Task("Walk", 20)
    owner.pets[0].add_task(walk)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(walk, TODAY)
    second = scheduler.mark_task_complete(walk, TODAY)

    assert second is None
    assert len(owner.pets[0].tasks) == 2  # the original plus one copy for tomorrow


def test_completed_and_future_tasks_are_left_out_of_todays_plan():
    owner = make_owner()
    owner.pets[0].add_task(Task("Done walk", 20, completed=True))
    owner.pets[0].add_task(Task("Tomorrow's walk", 20, due_date=date(2026, 10, 26)))
    owner.pets[0].add_task(Task("Overdue bath", 30, due_date=date(2026, 10, 20)))

    plan = Scheduler(owner).generate_plan(TODAY)

    assert [task.title for _, task, _ in plan] == ["Overdue bath"]


def test_detect_conflicts_same_pet_same_time():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, preferred_time="07:30"))
    owner.pets[0].add_task(Task("Breakfast", 10, preferred_time="07:30"))
    scheduler = Scheduler(owner)

    scheduler.generate_plan(TODAY)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "both for Mochi" in warnings[0]


def test_detect_conflicts_partial_overlap():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, preferred_time="07:30"))  # 07:30-08:00
    owner.pets[1].add_task(Task("Pill", 5, preferred_time="07:45"))  # inside the walk
    scheduler = Scheduler(owner)

    scheduler.generate_plan(TODAY)

    assert len(scheduler.detect_conflicts()) == 1


def test_untimed_tasks_fill_gaps_without_overlapping_timed_ones():
    owner = make_owner()
    owner.pets[0].add_task(Task("Walk", 30, "high", preferred_time="08:10"))
    owner.pets[0].add_task(Task("Play", 20, "medium"))  # too long for 08:00-08:10
    owner.pets[1].add_task(Task("Feed", 10, "high"))  # fits 08:00-08:10 exactly
    scheduler = Scheduler(owner, day_start="08:00")

    plan = scheduler.generate_plan(TODAY)

    assert [(start, task.title) for start, task, _ in plan] == [
        ("08:00", "Feed"),
        ("08:10", "Walk"),
        ("08:40", "Play"),
    ]
    assert scheduler.detect_conflicts() == []


def test_zero_minutes_available_skips_everything():
    owner = make_owner(minutes=0)
    owner.pets[0].add_task(Task("Walk", 20, "high"))
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan(TODAY) == []
    assert [task.title for task, _ in scheduler.skipped] == ["Walk"]


def test_edit_task_rejects_unknown_field():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 20))

    with pytest.raises(AttributeError):
        pet.edit_task("Walk", {"colour": "blue"})
