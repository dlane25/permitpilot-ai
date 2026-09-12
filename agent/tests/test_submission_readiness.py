from __future__ import annotations

import unittest

from permitpilot.models import ProjectInput, WorkflowStatus
from permitpilot.tools import calculate_submission_readiness
from permitpilot.workflow import create_submission_readiness_workflow_result


class SubmissionReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
            project_id="PP-OR-001",
            name="Oak Ridge Residence",
            address="1842 Oak Ridge Drive, Houston, TX",
            jurisdiction="Houston, Texas",
            project_type="New single-family residence",
            goal="Prepare this project for permit submission.",
        )

    def test_missing_item_blocks_submission(self) -> None:
        result = calculate_submission_readiness(
            compliance_results=[
                {
                    "requirement": "Required document",
                    "status": "missing",
                    "remediation": "Add document.",
                }
            ]
        )

        self.assertFalse(result["ready_for_submission"])
        self.assertEqual(result["blocking_count"], 1)

    def test_satisfied_items_can_be_submission_ready(self) -> None:
        result = calculate_submission_readiness(
            compliance_results=[
                {
                    "requirement": "Required document",
                    "status": "satisfied",
                    "remediation": None,
                }
            ]
        )

        self.assertTrue(result["ready_for_submission"])
        self.assertEqual(result["readiness_score"], 100)

    def test_conditional_item_is_not_blocking(self) -> None:
        result = calculate_submission_readiness(
            compliance_results=[
                {
                    "requirement": "Scope review",
                    "status": "conditional",
                    "remediation": "Confirm scope.",
                }
            ]
        )

        self.assertTrue(result["ready_for_submission"])
        self.assertEqual(result["non_blocking_count"], 1)

    def test_oak_ridge_enters_readiness_review(self) -> None:
        result = create_submission_readiness_workflow_result(self.project)

        self.assertEqual(
            result.status,
            WorkflowStatus.READINESS_REVIEW,
        )
        self.assertIsNotNone(result.submission_readiness)
        self.assertFalse(
            result.submission_readiness.ready_for_submission
        )
        self.assertGreater(
            result.submission_readiness.blocking_count,
            0,
        )

    def test_oak_ridge_has_prioritized_remediation(self) -> None:
        result = create_submission_readiness_workflow_result(self.project)

        self.assertGreater(
            len(result.submission_readiness.remediation_actions),
            0,
        )

        priorities = [
            item.priority
            for item in result.submission_readiness.remediation_actions
        ]

        self.assertEqual(
            priorities,
            list(range(1, len(priorities) + 1)),
        )

    def test_readiness_decision_preserves_human_control(self) -> None:
        result = create_submission_readiness_workflow_result(self.project)

        self.assertIsNotNone(result.decision)
        self.assertEqual(
            result.decision.approval_state.value,
            "pending",
        )


if __name__ == "__main__":
    unittest.main()
