# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I used Copilot to help brainstorm and draft a four-class UML diagram saved in `uml_draft.md`. The core relationship is: an Owner owns many Pets, each Pet holds many Tasks, and a Scheduler reads from the Owner to build a daily plan.

The four classes and their responsibilities:

- **Task** (dataclass): Stores everything about a single care activity — title, duration, priority, scheduled time, recurrence frequency, completion status, and which pet it belongs to. Responsible for determining if it fits in available time and managing its own completion/rescheduling.
- **Pet** (dataclass): Holds a pet's profile (name, species, age, special needs) and its own list of tasks. Responsible for tagging tasks with the pet's name when they are added.
- **Owner**: Manages a collection of pets and a master task list. Acts as the single source of truth for all care data; provides filtered views such as tasks for a specific pet.
- **Scheduler**: The "brain" of the system. Reads from the Owner to build a time-sorted, priority-ordered daily plan; also handles filtering, conflict detection, and producing a human-readable schedule explanation.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, one notable change emerged during implementation. In the initial skeleton, tasks were stored only on the Owner's master task list. After reviewing the design with Copilot, I moved the primary task list onto Pet, so each pet owns its tasks directly. The Owner then provides an `all_tasks()` helper that aggregates across all pets. This made filtering by pet much cleaner and better reflected the real-world relationship — a walk belongs to Mochi, not just to Jordan.

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
