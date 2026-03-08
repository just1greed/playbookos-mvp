from decimal import Decimal

from playbookos.domain.models import Goal, Reflection, RiskLevel, Run, Task


def test_goal_requires_basic_fields() -> None:
    goal = Goal(
        title="Launch onboarding workflow",
        objective="Automate employee onboarding checklist execution",
        definition_of_done=["First run succeeds"],
        risk_level=RiskLevel.HIGH,
        budget_amount=Decimal("1500.00"),
    )

    assert goal.status.value == "draft"
    assert goal.risk_level.value == "high"


def test_task_and_run_defaults() -> None:
    task = Task(
        goal_id="goal-1",
        playbook_id="playbook-1",
        name="Provision accounts",
        description="Create accounts and collect outputs",
    )
    run = Run(task_id=task.id, worker_type="agents-sdk")

    assert task.status.value == "inbox"
    assert run.status.value == "queued"
    assert run.attempt == 1


def test_reflection_requires_summary() -> None:
    reflection = Reflection(
        run_id="run-1",
        failure_category="tool-timeout",
        summary="Add retry and better preflight validation",
        proposal={"change": "increase retry budget"},
    )

    assert reflection.eval_status.value == "proposed"
    assert reflection.approval_status == "pending"
