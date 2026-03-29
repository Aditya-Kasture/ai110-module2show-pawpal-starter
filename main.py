"""Demo script — verify PawPal+ scheduling logic in the terminal."""
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Setup ---
    owner = Owner("Jordan", available_minutes_per_day=120)

    mochi = Pet("Mochi", "dog", 3.0)
    luna = Pet("Luna", "cat", 5.0, special_needs=["senior diet"])
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk",  30, "high",   time="07:00", frequency="daily",  due_date=date.today()))
    mochi.add_task(Task("Feed breakfast", 10, "high",  time="07:30"))
    mochi.add_task(Task("Playtime",       20, "medium", time="10:00"))
    mochi.add_task(Task("Evening walk",   30, "high",   time="18:00", frequency="daily",  due_date=date.today()))

    luna.add_task(Task("Feed breakfast",   5, "high",   time="07:30"))
    luna.add_task(Task("Medication",       5, "high",   time="08:00", notes="Half pill with food"))
    luna.add_task(Task("Vet appointment", 60, "medium", time="14:00"))
    luna.add_task(Task("Grooming",        25, "low",    time="11:00"))

    scheduler = Scheduler(owner)

    # --- Today's schedule ---
    print("=" * 45)
    print(scheduler.explain_plan())

    # --- All tasks sorted by time ---
    print("\n--- All tasks by time ---")
    for task in scheduler.sort_by_time():
        pet_label = f"[{task.pet_name}] " if task.pet_name else ""
        status = "✓" if task.is_complete else "○"
        print(f"  {task.time}  {status}  {pet_label}{task.title}"
              f"  ({task.duration_minutes} min, {task.priority})")

    # --- Filter by pet ---
    print("\n--- Mochi's tasks ---")
    for task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task.title} at {task.time}")

    # --- Conflict detection ---
    print("\n--- Conflict check ---")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts detected.")

    # --- Recurring task demo ---
    print("\n--- Recurring task demo ---")
    walk = mochi.tasks[0]
    print(f"  Before: {walk.title} due {walk.due_date}, complete={walk.is_complete}")
    scheduler.mark_task_complete(walk)
    print(f"  After:  {walk.title} due {walk.due_date}, complete={walk.is_complete}")


if __name__ == "__main__":
    main()
