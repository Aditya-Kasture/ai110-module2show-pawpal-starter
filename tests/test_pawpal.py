"""Automated tests for PawPal+ core logic."""
from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_once_sets_flag():
    task = Task("Feed", 10, "high", frequency="once")
    task.mark_complete()
    assert task.is_complete is True


def test_mark_complete_daily_advances_due_date():
    today = date.today()
    task = Task("Walk", 30, "high", frequency="daily", due_date=today)
    task.mark_complete()
    assert task.due_date == today + timedelta(days=1)
    assert task.is_complete is False  # recurring — not done, just rescheduled


def test_mark_complete_weekly_advances_due_date():
    today = date.today()
    task = Task("Bath", 30, "medium", frequency="weekly", due_date=today)
    task.mark_complete()
    assert task.due_date == today + timedelta(weeks=1)
    assert task.is_complete is False


def test_is_schedulable_fits():
    task = Task("Walk", 30, "high")
    assert task.is_schedulable(30) is True
    assert task.is_schedulable(60) is True


def test_is_schedulable_does_not_fit():
    task = Task("Walk", 30, "high")
    assert task.is_schedulable(29) is False


def test_priority_rank_values():
    assert Task("a", 5, "high").priority_rank() == 3
    assert Task("b", 5, "medium").priority_rank() == 2
    assert Task("c", 5, "low").priority_rank() == 1


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog", 3.0)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 30, "high"))
    assert len(pet.tasks) == 1


def test_add_task_sets_pet_name():
    pet = Pet("Luna", "cat", 5.0)
    task = Task("Feed", 5, "high")
    pet.add_task(task)
    assert task.pet_name == "Luna"


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_sort_by_time_is_chronological():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    pet.add_task(Task("Evening walk", 30, "high",   time="18:00"))
    pet.add_task(Task("Morning walk", 30, "high",   time="07:00"))
    pet.add_task(Task("Lunch snack",   5, "medium", time="12:00"))

    times = [t.time for t in Scheduler(owner).sort_by_time()]
    assert times == sorted(times)


def test_build_plan_respects_available_time():
    owner = Owner("Jordan", available_minutes_per_day=60)
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    pet.add_task(Task("Walk",     30, "high", time="07:00"))
    pet.add_task(Task("Grooming", 45, "low",  time="10:00"))

    plan = Scheduler(owner).build_plan()
    assert sum(t.duration_minutes for t in plan) <= 60


def test_build_plan_prefers_high_priority():
    owner = Owner("Jordan", available_minutes_per_day=30)
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    pet.add_task(Task("Low task",  30, "low",  time="08:00"))
    pet.add_task(Task("High task", 30, "high", time="09:00"))

    plan = Scheduler(owner).build_plan()
    assert len(plan) == 1
    assert plan[0].title == "High task"


def test_detect_conflicts_flags_same_time():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", time="07:00"))
    pet.add_task(Task("Feed", 10, "high", time="07:00"))

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "07:00" in conflicts[0]


def test_no_conflicts_when_times_differ():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", time="07:00"))
    pet.add_task(Task("Feed", 10, "high", time="08:00"))

    assert Scheduler(owner).detect_conflicts() == []


def test_filter_by_pet_returns_correct_tasks():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", 3.0)
    luna = Pet("Luna", "cat", 5.0)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Walk", 30, "high"))
    luna.add_task(Task("Feed",  5, "high"))

    mochi_tasks = Scheduler(owner).filter_by_pet("Mochi")
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].pet_name == "Mochi"


def test_filter_by_status():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3.0)
    owner.add_pet(pet)
    done = Task("Walk", 30, "high", is_complete=True)
    pending = Task("Feed", 10, "high", is_complete=False)
    pet.add_task(done)
    pet.add_task(pending)

    s = Scheduler(owner)
    assert len(s.filter_by_status(True)) == 1
    assert len(s.filter_by_status(False)) == 1
