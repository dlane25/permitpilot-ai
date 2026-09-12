from __future__ import annotations

import unittest

from permitpilot.models import (
    ApplicabilityClassification,
    ProjectInput,
    WorkflowStatus,
)
from permitpilot.tools import analyze_permit_applicability
from permitpilot.workflow import create_applicability_workflow_result


class PermitApplicabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
            project_id="PP-OR-001",
            name="Oak Ridge Residence",
            address="1842 Oak Ridge Drive, Houston, TX",
            jurisdiction="Houston, Texas",
            project_type="New single-family residence",
            goal="Prepare this project for permit submission.",
        )

    def test_building_permit_is_applicable(self) -> None:
        result = analyze_permit_applicability(
            project_type=self.project.project_type,
            jurisdiction=self.project.jurisdiction or "",
            requirements=[
                "A building permit is required for most residential projects "
                "inside the corporate City of Houston limits."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "applicable",
        )

    def test_scope_dependent_requirement_is_conditional(self) -> None:
        result = analyze_permit_applicability(
            project_type=self.project.project_type,
            jurisdiction=self.project.jurisdiction or "",
            requirements=[
                "Electrical review may be required depending on project scope."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "conditional",
        )

    def test_portal_capability_is_not_applicable(self) -> None:
        result = analyze_permit_applicability(
            project_type=self.project.project_type,
            jurisdiction=self.project.jurisdiction or "",
            requirements=[
                "The City permit portal supports permit applications."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "not_applicable",
        )

    def test_ambiguous_requirement_requires_human_review(self) -> None:
        result = analyze_permit_applicability(
            project_type=self.project.project_type,
            jurisdiction=self.project.jurisdiction or "",
            requirements=[
                "Additional documentation should be provided when appropriate."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "needs_human_review",
        )

    def test_oak_ridge_workflow_reaches_applicability_ready(self) -> None:
        result = create_applicability_workflow_result(self.project)

        self.assertEqual(
            result.status,
            WorkflowStatus.APPLICABILITY_READY,
        )

        self.assertIsNotNone(result.applicability_analysis)
        self.assertGreater(
            result.applicability_analysis.applicable_count,
            0,
        )
        self.assertGreater(
            result.applicability_analysis.conditional_count,
            0,
        )
        self.assertEqual(
            result.applicability_analysis.needs_human_review_count,
            0,
        )

    def test_each_determination_preserves_source_evidence(self) -> None:
        result = create_applicability_workflow_result(self.project)

        analysis = result.applicability_analysis
        self.assertIsNotNone(analysis)

        for determination in analysis.determinations:
            self.assertIsNotNone(determination.source_name)
            self.assertIsNotNone(determination.source_url)

    def test_classification_enum_contains_expected_values(self) -> None:
        self.assertEqual(
            ApplicabilityClassification.APPLICABLE.value,
            "applicable",
        )
        self.assertEqual(
            ApplicabilityClassification.CONDITIONAL.value,
            "conditional",
        )
        self.assertEqual(
            ApplicabilityClassification.NOT_APPLICABLE.value,
            "not_applicable",
        )
        self.assertEqual(
            ApplicabilityClassification.NEEDS_HUMAN_REVIEW.value,
            "needs_human_review",
        )


if __name__ == "__main__":
    unittest.main()
