from __future__ import annotations

import unittest

from permitpilot.models import ProjectInput, WorkflowStatus
from permitpilot.tools import apply_approved_remediation
from permitpilot.workflow import create_remediation_execution_workflow_result


class RemediationExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
            project_id="PP-OR-001",
            name="Oak Ridge Residence",
            address="1842 Oak Ridge Drive, Houston, TX",
            jurisdiction="Houston, Texas",
            project_type="New single-family residence",
            goal="Prepare this project for permit submission.",
        )

        self.approved_updates = [
            {
                "document_type": "wastewater_capacity_letter",
                "approved": True,
                "present": True,
                "status": "complete",
            },
            {
                "document_type": "prerequisite_checklist",
                "approved": True,
                "present": True,
                "status": "complete",
            },
        ]

    def test_unapproved_update_is_rejected(self) -> None:
        result = apply_approved_remediation(
            documents=[
                {
                    "document_id": "DOC-X",
                    "name": "Test Document",
                    "document_type": "test_document",
                    "present": False,
                    "status": "missing",
                }
            ],
            approved_updates=[
                {
                    "document_type": "test_document",
                    "approved": False,
                    "present": True,
                    "status": "complete",
                }
            ],
        )

        self.assertEqual(result["applied_count"], 0)
        self.assertEqual(result["rejected_count"], 1)
        self.assertFalse(result["documents"][0]["present"])

    def test_approved_updates_are_applied(self) -> None:
        result = create_remediation_execution_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertEqual(
            result.remediation_execution.applied_count,
            2,
        )
        self.assertEqual(
            result.remediation_execution.rejected_count,
            0,
        )

    def test_execution_records_audit_events(self) -> None:
        result = create_remediation_execution_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertEqual(
            len(result.remediation_execution.audit_events),
            2,
        )

        for event in result.remediation_execution.audit_events:
            self.assertEqual(event.outcome, "applied")
            self.assertTrue(event.approved)

    def test_remediation_removes_submission_blockers(self) -> None:
        result = create_remediation_execution_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertEqual(
            result.submission_readiness.blocking_count,
            0,
        )
        self.assertTrue(
            result.submission_readiness.ready_for_submission
        )

    def test_workflow_reaches_ready_for_submission(self) -> None:
        result = create_remediation_execution_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertEqual(
            result.status,
            WorkflowStatus.READY_FOR_SUBMISSION,
        )

    def test_final_submission_still_requires_human_approval(self) -> None:
        result = create_remediation_execution_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertIsNotNone(result.decision)
        self.assertEqual(
            result.decision.approval_state.value,
            "pending",
        )
        self.assertEqual(
            result.next_action,
            "Request final human approval to submit permit package.",
        )


if __name__ == "__main__":
    unittest.main()
