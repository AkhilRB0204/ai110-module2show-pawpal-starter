# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Core user actions, based on the PawPal+ scenario:

1. **Enter owner and pet information.** The user can set up a profile with basic details about themselves (name, how much time they have each day, any preferences) and about their pet (name, species/breed, any special needs). The scheduler uses this context when building a plan.
2. **Add and manage care tasks.** The user can add care tasks for their pet, such as a walk, feeding, medication, grooming, or enrichment. Each task has at least a duration and a priority, and the user can edit or remove a task later as their routine changes.
3. **Generate and view today's plan.** The user can ask PawPal+ to build a daily schedule that fits the tasks into the time available, putting higher-priority tasks first. The app shows the plan clearly, explains why it chose that order, and notes any tasks it had to leave out.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code as an agent for most of the design and implementation steps:

- **Design brainstorming:** I asked it to identify the core user actions from the README scenario and to brainstorm the objects, attributes, and methods the system needed.
- **UML:** it turned the brainstorm into a Mermaid class diagram, then reviewed that diagram for relationships that didn't make sense and for unnecessary complexity.
- **Code generation:** it generated the class skeletons in `pawpal_system.py` (using dataclasses for `Task`, `Pet`, and `Owner`), then the full scheduling logic, the `main.py` demo, and the pytest tests.

The most helpful prompts were specific and tied to an artifact that already existed, for example "based on my UML, generate class skeletons" or "review the diagram and remove unnecessary complexity." Open-ended prompts tended to produce more than I needed.

**b. Judgment and verification**

- **Rejected a fifth class.** The first brainstorm suggested a separate `DailyPlan` class to hold the schedule and its explanations. My design called for four classes, so I folded that job into `Scheduler` (its `plan` and `skipped` lists plus `explain_plan()`).
- **Trimmed the first UML.** The first version had redundant pieces: a `Scheduler.collect_tasks()` method that duplicated `Owner.get_all_tasks()`, getter and setter methods that only wrapped public attributes, and fields such as `age`, `special_needs`, and `category` that no method used. I had these removed so the design only holds what the scheduler needs.
- **Kept the Scheduler reading from the Owner.** I checked that `generate_plan()` gets its tasks through `Owner.get_all_tasks()` rather than from a single pet, so the plan covers every pet.

To verify the result, I ran `python main.py` and checked the printed schedule by hand: tasks with a preferred time landed at that time, other tasks filled the gaps without overlapping, and the 45-minute bath was skipped once only 30 minutes were left. I also ran `python -m pytest`, and all 4 tests passed: task completion, task addition, planning across both pets, and skipping tasks that don't fit.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
