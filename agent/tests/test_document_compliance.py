from __future__ import annotations

import unittest

from permitpilot.models import ProjectInput, WorkflowStatus
from permitpilot.workflow import create_document_compliance_workflow_result


class DocumentComplianceWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
            project_id="PP-OR-001",
            name="Oak Ridge Residence",
            address="1842 Oak Ridge Drive, Houston, TX",
            jurisdiction="Houston, Texas",
            project_type="New single-family residence",
            goal="Prepare this project for permit submission.",
        )

    def test_document_compliance_finds_missing_items(self) -> None:
        result = create_document_compliance_workflow_result(self.project)

        self.assertIsNotNone(result.document_compliance)
        self.assertGreater(
            result.document_compliance.missing_count,
            0,
        )

    def test_document_compliance_finds_partial_items(self) -> None:
        result = create_document_compliance_workflow_result(self.project)

        self.assertGreaterEqual(
            result.document_compliance.partial_count,
            0,
        )

    def test_missing_documents_trigger_decision_required(self) -> None:
        result = create_document_compliance_workflow_result(self.project)

        self.assertEqual(
            result.status,
            WorkflowStatus.DECISION_REQUIRED,
        )
        self.assertIsNotNone(result.decision)

    def test_compliance_preserves_source_evidence(self) -> None:
        result = create_document_compliance_workflow_result(self.project)

        for check in result.document_compliance.results:
            if check.document_type is not None:
                self.assertIsNotNone(check.source_name)
                self.assertIsNotNone(check.source_url)

    def test_next_action_is_remediation(self) -> None:
        result = create_document_compliance_workflow_result(self.project)

        self.assertEqual(
            result.next_action,
            "Resolve missing and incomplete permit documents.",
        )


if __name__ == "__main__":
    unittest.main()
