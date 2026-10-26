"""Demo script: build a sample owner with two pets and exercise the scheduler."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task, to_hhmm, to_minutes


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a heading and one line per task."""
    print(f"\n{heading}")
    for t in tasks:
        status = "done" if t.completed else "todo"
        when = t.preferred_time or "--:--"
        due = f" due {t.due_date}" if t.due_date else ""
        print(f"  {when}  {t.title:<18} {t.pet_name:<6} {t.frequency:<7} {status}{due}")


def main() -> None:
    today = date(2026, 10, 25)
    owner = Owner(name="Jordan", available_minutes=120)

    # Tasks are added out of time order on purpose to show sorting.
    mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu")
    mochi.add_task(Task("Fetch in the yard", 20, "medium", preferred_time="17:00"))
    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="07:30"))
    mochi.add_task(Task("Breakfast", 10, "high", preferred_time="07:00"))
    mochi.add_task(Task("Bath", 45, "low", frequency="weekly"))

    luna = Pet(name="Luna", species="cat")
    luna.add_task(Task("Brush coat", 15, "medium", preferred_time="12:00"))
    luna.add_task(Task("Clean litter box", 10, "medium", preferred_time="09:00"))
    # Same time as Mochi's morning walk, to trigger a conflict warning.
    luna.add_task(Task("Thyroid pill", 5, "high", preferred_time="07:30"))

    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner, day_start="07:00")

    print_tasks("All tasks, as added:", owner.get_all_tasks())
    print_tasks("Sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
    print_tasks("Only Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))

    # Recurring tasks: completing a daily task schedules tomorrow's copy.
    breakfast = mochi.tasks[2]
    next_breakfast = scheduler.mark_task_complete(breakfast, today)
    print(f"\nCompleted {breakfast.title}; next one is due {next_breakfast.due_date}.")
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks("Still to do:", scheduler.filter_tasks(completed=False))

    plan = scheduler.generate_plan(today)
    print(f"\nToday's Schedule for {owner.name}'s pets ({today})")
    print("=" * 62)
    for start, task, reason in plan:
        end = to_hhmm(to_minutes(start) + task.duration)
        print(f"{start}-{end}  {task.title:<18} {task.pet_name:<6} [{reason}]")
    print("=" * 62)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
