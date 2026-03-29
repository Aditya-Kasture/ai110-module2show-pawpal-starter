# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I used Copilot to help brainstorm and draft a four-class UML diagram saved in `uml_draft.md`. The core relationship is: an Owner owns many Pets, each Pet holds many Tasks, and a Scheduler reads from the Owner to build a daily plan.

The four classes and their responsibilities:

- **Task** (dataclass): Stores everything about a single care activity - title, duration, priority, scheduled time, recurrence frequency, completion status, and which pet it belongs to. Responsible for determining if it fits in available time and managing its own completion/rescheduling.
- **Pet** (dataclass): Holds a pet's profile (name, species, age, special needs) and its own list of tasks. Responsible for tagging tasks with the pet's name when they are added.
- **Owner**: Manages a collection of pets and a master task list. Acts as the single source of truth for all care data; provides filtered views such as tasks for a specific pet.
- **Scheduler**: The "brain" of the system. Reads from the Owner to build a time-sorted, priority-ordered daily plan; also handles filtering, conflict detection, and producing a human-readable schedule explanation.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, one notable change emerged during implementation. In the initial skeleton, tasks were stored only on the Owner's master task list. After reviewing the design with Copilot, I moved the primary task list onto Pet, so each pet owns its tasks directly. The Owner then provides an `all_tasks()` helper that aggregates across all pets. This made filtering by pet much cleaner and better reflected the real-world relationship: a walk belongs to Mochi, not just to Jordan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two main constraints: available time per day (in minutes) and task priority (high, medium, low). It sorts all tasks by priority rank first, then greedily adds tasks until the owner's available time is exhausted. I decided that time was the hard constraint (you simply cannot schedule more than the day allows) and priority was the ordering rule within that limit, since a pet's medication or feeding should always come before optional grooming.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler only detects exact time conflicts (two tasks at the identical HH:MM) rather than checking for overlapping durations. For example, a 30-minute walk starting at 07:00 and a 10-minute feed starting at 07:15 would not be flagged, even though they overlap. This is a reasonable tradeoff for a basic pet care planner because it keeps the logic simple and readable, and most real-world pet tasks are short enough that owners naturally space them out. A future iteration could calculate end times and check for true overlap, but that added complexity is not necessary for the core use case.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Copilot throughout the project in a structured, phase-by-phase way following the assignment instructions. In Phase 1, I used it to brainstorm the four classes and generate the Mermaid UML diagram. In Phase 2, I used Agent mode to flesh out the full implementation of `pawpal_system.py` and generate the test suite in `tests/test_pawpal.py`. In Phase 3, I used it to understand how `st.session_state` works and to wire the UI to the backend logic. The most helpful prompts were specific and scoped, for example, asking Copilot to review a single file with `#file:pawpal_system.py` and asking targeted questions like "how should the Scheduler retrieve tasks from the Owner's pets?" rather than broad open-ended requests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When Copilot initially suggested storing tasks only on the Owner object, I reviewed the design and felt it did not accurately represent the relationship between pets and their care activities. A walk belongs to Mochi, not just to Jordan. I pushed back and restructured so that each Pet holds its own task list, with Owner providing an `all_tasks()` aggregator. I verified the change by running the full test suite (`python -m pytest`) and confirming that filtering by pet, conflict detection, and schedule generation all still produced correct results.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 15 automated tests covering: `mark_complete()` correctly setting the completion flag for one-time tasks and advancing the due date for daily/weekly recurring tasks; `is_schedulable()` returning the right boolean based on available time; `priority_rank()` returning correct numeric values; adding a task to a Pet increasing the task count and tagging the task with the pet's name; `sort_by_time()` returning tasks in chronological order regardless of insertion order; `build_plan()` respecting the available-time limit and preferring high-priority tasks; `detect_conflicts()` flagging exact time matches and staying silent when times differ; and `filter_by_pet()` and `filter_by_status()` returning only matching tasks. These tests were important because they verified the core logic independently of the UI. If the backend is wrong, no amount of UI polish fixes it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident the scheduler handles the scenarios covered by the test suite correctly. All 15 tests pass. Given more time, I would test the following edge cases: an owner with zero available time (empty plan); two pets with tasks at the same time (cross-pet conflict); a recurring task with no due_date set (the rescheduling logic currently skips the date advance); and a task whose duration exactly equals the remaining available time (boundary condition for `is_schedulable`).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the test suite. Following the project instructions to write tests before integrating the UI forced me to think clearly about what each method was supposed to do in isolation. The result was that when I wired `app.py` to the backend in Phase 3, there were no surprises. The logic already worked and the UI just had to call it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the conflict detection to check for overlapping durations rather than only exact time matches. As it stands, a 30-minute walk at 07:00 and a feeding at 07:15 are not flagged, even though they overlap. I would calculate each task's end time (`start + duration`) and flag any pair where one task's window intersects another's. I would also add data persistence so that the owner's pets and tasks survive a Streamlit page refresh.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI tools like Copilot are most effective when you give them a clear, bounded scope and then critically review the output before accepting it. Asking Copilot to generate an entire system at once produces code that is hard to evaluate. Asking it to help with one class, one method, or one phase at a time (as the project instructions required) made it easy to spot gaps, push back on suggestions that did not fit the design, and stay in control of the architecture throughout.
