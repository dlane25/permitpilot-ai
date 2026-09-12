from __future__ import annotations

import unittest

from permitpilot.tools import analyze_permit_applicability


class PermitApplicabilityRegressionTests(unittest.TestCase):
    def test_projectdox_submission_is_applicable(self) -> None:
        result = analyze_permit_applicability(
            project_type="New single-family residence",
            jurisdiction="Houston, Texas",
            requirements=[
                "Plans and required documents are submitted electronically "
                "through the City's permitting workflow and ProjectDox."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "applicable",
        )

    def test_site_development_documents_are_conditional(self) -> None:
        result = analyze_permit_applicability(
            project_type="New single-family residence",
            jurisdiction="Houston, Texas",
            requirements=[
                "A building permit application and complete set of plans "
                "are required for residential site development review."
            ],
        )

        self.assertEqual(
            result["determinations"][0]["classification"],
            "conditional",
        )


if __name__ == "__main__":
    unittest.main()
