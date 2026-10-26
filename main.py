"""Demo script: build a sample owner with two pets and print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task, to_hhmm, to_minutes


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=120)

    mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu")
    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="07:30"))
    mochi.add_task(Task("Breakfast", 10, "high"))
    mochi.add_task(Task("Fetch in the yard", 20, "medium"))
    mochi.add_task(Task("Bath", 45, "low", frequency="weekly"))

    luna = Pet(name="Luna", species="cat")
    luna.add_task(Task("Thyroid pill", 5, "high", preferred_time="08:00"))
    luna.add_task(Task("Brush coat", 15, "medium"))
    luna.add_task(Task("Clean litter box", 10, "medium"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner, day_start="07:00")
    plan = scheduler.generate_plan()

    print(f"Today's Schedule for {owner.name}'s pets")
    print("=" * 62)
    for start, task, reason in plan:
        end = to_hhmm(to_minutes(start) + task.duration)
        print(f"{start}-{end}  {task.title:<18} {task.pet_name:<6} [{reason}]")
    print("=" * 62)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
