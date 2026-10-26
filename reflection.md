# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Core user actions, based on the PawPal+ scenario:

1. **Enter owner and pet information.** The user can set up a profile with basic details about themselves (name, how much time they have each day, any preferences) and about their pet (name, species/breed, any special needs). The scheduler uses this context when building a plan.
2. **Add and manage care tasks.** The user can add care tasks for their pet, such as a walk, feeding, medication, grooming, or enrichment. Each task has at least a duration and a priority, and the user can edit or remove a task later as their routine changes.
3. **Generate and view today's plan.** The user can ask PawPal+ to build a daily schedule that fits the tasks into the time available, putting higher-priority tasks first. The app shows the plan clearly, explains why it chose that order, and notes any tasks it had to leave out.

My initial UML had four classes. `Owner` held the owner's name, how many minutes they had that day, their preferences, and their list of pets. `Pet` held the pet's details and its own list of tasks. `Task` was one care activity with a title, duration, priority, frequency, and an optional preferred time. `Scheduler` was the "brain" that took an owner and built the daily plan: sorting tasks, dropping the ones that didn't fit, detecting conflicts, and explaining the result.

The relationships were simple: an owner has pets, a pet has tasks, and the scheduler plans for an owner. I kept the data in the first three classes and all the decision-making in `Scheduler`, so each class had one job.

**b. Design changes**

Yes, in a few ways (the final version is in `diagrams/uml_final.mmd`).

- **Recurring tasks changed `Task`.** At first I tracked `last_completed` to decide when a task was due again. When I added automatic recurrence, I switched to a `due_date` field. Completing a task now creates a new copy with `due_date = today + timedelta(days=1)` (or 7 days for weekly), which is easier to understand and test.
- **`Task` got a `pet_name`.** Once the scheduler mixed tasks from every pet into one plan, the output needed to say whose task each one was, so `Pet.add_task()` stamps the pet's name on it.
- **The Scheduler's methods got clearer names.** The draft had `sort_tasks` and `filter_tasks`, where "filter" meant "fit into the time budget". When I added filtering by pet and status, that name was confusing, so I split things into `sort_by_priority`, `sort_by_time`, `filter_tasks` (pet and status), and `fit_to_time` (budget). I also added `mark_task_complete()` and `Owner.get_pet()` for recurrence.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:

- **Time available:** the owner's minutes for the day. This is a hard limit, and tasks that don't fit are skipped with a reason.
- **Priority:** high, then medium, then low decides who gets time first. Ties go to the shorter task, so more things fit.
- **Preferred time:** a task with a set time is placed exactly there.
- **Due date and completion:** finished tasks and future copies of recurring tasks stay out of today's plan, and overdue ones stay in.

I ranked them by what would hurt a pet most if it went wrong. Missing a medication or a meal is worse than skipping a bath, so priority decides what makes the cut. Time is next because it's the real-world limit: an owner can't do 3 hours of tasks in 1 hour. Preferred times come after that, since they decide when a task happens but not whether it happens. I didn't use the owner's `preferences` dictionary in the algorithm yet, because the three constraints above already covered what the scenario asked for.

**b. Tradeoffs**

My scheduler warns about conflicts but doesn't fix them. If two tasks have overlapping preferred times (like Mochi's 07:30 walk and Luna's 07:30 pill), it still puts both at 07:30 and adds a warning instead of moving one of them. It does check for overlapping time ranges and not just exact matches, so a 30-minute walk at 07:30 and a pill at 07:45 also get flagged.

I think that's reasonable for a pet owner. A preferred time usually means something real, like a pill that has to be given with breakfast, and the scheduler doesn't know which task is safe to move. Some overlaps are fine anyway, since you can give a cat a pill while the dog is waiting by the door. A warning lets the owner decide, and it never crashes the app.

A second tradeoff is that the time budget is filled greedily: highest priority first, then shortest. That's easy to explain, but it doesn't always fill the day perfectly. In my demo the 45-minute bath is skipped even though 40 minutes are free, and a smarter algorithm might swap tasks around to fit more in.

When I asked the AI to simplify `detect_conflicts()`, it suggested two things. The first was using `itertools.combinations` to loop over every pair instead of nested loops with index slicing. I kept that because it's shorter and actually easier to read. The second was sorting by start time and doing a single sweep, which would be faster for huge lists. I didn't use that one because it's harder to follow, and a pet owner will only have maybe 5 to 20 tasks a day, so checking every pair is plenty fast.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code for pretty much every step of this phase. First I had it read the README scenario and pick out the three main things a user needs to do. Then I used it to brainstorm the classes and what each one should store and do, and to turn that into a Mermaid UML diagram. After that it wrote the class skeletons (with dataclasses for Task, Pet, and Owner), the actual scheduling logic, the main.py demo, and the tests.

The prompts that worked best were the ones that pointed at something I already had, like "use my UML to make the class skeletons" or "look at the diagram and cut anything unnecessary." When I was vague it gave me more than I needed.

**b. Judgment and verification**

I didn't take everything it suggested. Its first brainstorm had five classes, including a separate DailyPlan class, but the assignment is built around four, so I had that folded into the Scheduler instead. I also had it review the first UML and it found stuff that didn't need to be there: a collect_tasks() method that did the same thing as Owner.get_all_tasks(), getter/setter methods for attributes that were already public, and fields like age, special_needs, and category that nothing actually used. I cut all of those. I also made sure the Scheduler gets its tasks through Owner.get_all_tasks() and not from just one pet, since it needs to plan for all of them.

To check that it actually worked, I ran python main.py and went through the schedule myself. The walk and the pill showed up at their preferred times, the other tasks filled in around them without overlapping, and the bath got skipped because it was 45 minutes and there were only 30 left. I also ran python -m pytest and all 4 tests passed (the suite later grew to 22).

**c. AI strategy**

- **Most effective features.** Agent mode was the biggest help, because it could edit several files at once (`pawpal_system.py`, `main.py`, the tests, the README, and the UML) and then run `python main.py` and `pytest` itself to check the result. That loop caught a real bug: a test it wrote for completing the same task twice failed, and the fix went into `mark_task_complete()`. It also used Streamlit's built-in test runner to click through the app, so I knew the UI worked before opening it. Pointing it at existing files ("based on my UML...", "based on my skeletons...") gave much better results than open-ended questions.
- **A suggestion I rejected or modified.** The first design had a fifth class, `DailyPlan`, just to hold the schedule. I rejected it and kept the plan inside `Scheduler`, because the assignment is built around four classes and the extra class didn't add any behavior. Later, when simplifying `detect_conflicts()`, I kept the readable `itertools.combinations` version and rejected the faster sort-and-sweep one, because a pet owner only has a handful of tasks.
- **Chat sessions.** Honestly, I did most of this project in one long session instead of separate ones per phase. The upside was that the AI remembered earlier decisions, like the four-class design and which methods had been renamed. The downside was that the conversation got long, and I had to keep asking it what had already been done. Next time I'd start a new session for each phase (design, implementation, algorithms, testing) and paste in only the files that phase needs. That would keep each conversation focused and make it obvious which prompts produced which changes.
- **Being the lead architect.** The AI can write a whole class in seconds, so the hard part isn't typing code. It's deciding what the system should be. My job was to set the shape (four classes, the scheduler reads through `Owner.get_all_tasks()`), say no to extras, and check every result by running it. When I gave clear constraints, the AI did good work. When I didn't, it added things I didn't need. I learned that I have to own the design and the verification, even when I didn't write every line.

---

## 4. Testing and Verification

**a. What you tested**

I have 22 tests. They cover the basics (completing a task, adding a task to a pet), sorting by time, filtering by pet and status, recurring tasks (daily, weekly, and one-time), conflict detection (exact same time, partial overlap, and back-to-back tasks that shouldn't be flagged), and the scheduler itself (multiple pets, the time budget, skipping completed and future tasks, and filling gaps around timed tasks). I also tested edge cases like an owner with no pets, a pet with no tasks, and a budget of 0 minutes.

These mattered because the scheduler's whole job is to get the order and timing right, and a bug there wouldn't crash anything. It would just quietly give the owner a wrong plan. One of the edge-case tests actually caught a real bug: marking the same task complete twice created two copies for the next day. That could easily happen in the app with a double click, so I fixed `mark_task_complete()` to do nothing if the task is already done.

**b. Confidence**

I'd say 4 out of 5. Every core feature has passing tests, including the tricky cases. If I had more time I'd test and handle tasks that run past midnight (right now a task could be scheduled at "25:00"), invalid times like "25:99", and two tasks with the same title on one pet, because `remove_task()` removes all of them, including future copies of a recurring task.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the scheduler explains itself. It doesn't just print a list. It says why each task is where it is, what got left out and why, and which tasks clash. I'm also happy with the test suite, because writing edge-case tests found a real bug (duplicate copies when a task is completed twice) before anyone hit it in the app.

**b. What you would improve**

- **Use the owner's preferences.** Things like "walks in the morning" are stored but not used by the algorithm yet.
- **Help fix conflicts.** Offer to move a flexible task to the next free slot, instead of only warning.
- **Fix the known gaps.** Handle tasks that run past midnight, and give tasks an ID so `remove_task()` doesn't delete every task with the same title.
- **Save data.** Keep pets and tasks in a file so they survive closing the app, since `session_state` only lasts one session.

**c. Key takeaway**

Design first, then let the AI build. Having the UML and the four-class plan before writing code meant I could judge every AI suggestion against something concrete: does this fit the design, or is it extra? Without that, it would have been easy to accept whatever looked impressive and end up with a messy system I didn't fully understand.
