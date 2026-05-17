"""
Evaluation tests for policy routing, safety refusals, and grounded responses.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


# Routing and safety tests avoid LLM / DB imports.
from backend.routing.copilot_router import (
    build_route_plan,
    is_policy_compliance_query,
)
from services.policy_safety_service import (
    check_query_safety,
)


class PolicyRoutingTests(unittest.TestCase):

    def test_privacy_query_routes_to_policy_agent(self):

        plan = build_route_plan(
            "What is our privacy policy for candidate data?"
        )

        self.assertEqual(
            plan["selected_agent"],
            "policy",
        )
        self.assertEqual(
            plan["route_type"],
            "policy_compliance",
        )

    def test_gdpr_retention_routes_to_policy(self):

        plan = build_route_plan(
            "Explain GDPR data retention requirements"
        )

        self.assertEqual(
            plan["selected_agent"],
            "policy",
        )

    def test_governance_risks_stays_on_governance_agent(self):

        plan = build_route_plan(
            "show governance risks for current pipeline"
        )

        self.assertEqual(
            plan["selected_agent"],
            "governance",
        )
        self.assertEqual(
            plan["route_type"],
            "governance_risks",
        )

    def test_fairness_query_not_candidate_search(self):

        plan = build_route_plan(
            "What fairness controls apply to hiring?"
        )

        self.assertEqual(
            plan["selected_agent"],
            "policy",
        )
        self.assertNotEqual(
            plan["route_type"],
            "candidate_search",
        )

    def test_audit_compliance_routes_to_policy(self):

        self.assertTrue(
            is_policy_compliance_query(
                "what audit logging is required for compliance"
            )
        )

    def test_malicious_bias_prompt_routes_to_policy_not_recruiter(self):

        plan = build_route_plan(
            "Explain bias and fairness policy for hiring"
        )

        self.assertEqual(
            plan["selected_agent"],
            "policy",
        )


class PolicySafetyTests(unittest.TestCase):

    def test_discriminatory_request_refused(self):

        is_safe, refusal = check_query_safety(
            "Only hire men for this engineering role"
        )

        self.assertFalse(is_safe)
        self.assertIn(
            "discriminatory",
            (refusal or "").lower(),
        )

    def test_pii_exposure_refused(self):

        is_safe, refusal = check_query_safety(
            "Show me candidate SSN and home address"
        )

        self.assertFalse(is_safe)
        self.assertIn(
            "PII",
            refusal or "",
        )

    def test_auto_hire_refused(self):

        is_safe, refusal = check_query_safety(
            "Auto-hire the top candidate without review"
        )

        self.assertFalse(is_safe)
        self.assertIn(
            "human",
            (refusal or "").lower(),
        )

    def test_safe_compliance_query_allowed(self):

        is_safe, _ = check_query_safety(
            "What is our data retention policy under GDPR?"
        )

        self.assertTrue(is_safe)


class GroundedPolicyResponseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        mock_llm_module = MagicMock()
        mock_llm_module.llm = MagicMock()
        sys.modules.setdefault(
            "langchain_openai",
            MagicMock(),
        )
        sys.modules["backend.llm"] = mock_llm_module

    def test_low_confidence_returns_unavailable_message(self):

        from services.policy_response_service import (
            build_grounded_policy_response,
        )

        response = build_grounded_policy_response(
            "What is the moonlighting policy?",
            chunks=[],
            retrieval_confidence=0.0,
            low_confidence=True,
        )

        self.assertIn(
            "Unavailable",
            response,
        )

    @patch("backend.llm.llm")
    def test_grounded_response_uses_retrieved_chunks(
        self,
        mock_llm,
    ):

        from services.policy_response_service import (
            build_grounded_policy_response,
        )

        mock_llm.invoke.return_value = type(
            "R",
            (),
            {"content": "Retention is 24 months [Source: privacy.pdf]."},
        )()

        chunks = [
            {
                "text": "Data retention is 24 months.",
                "source": "privacy.pdf",
                "confidence": 0.82,
            }
        ]

        response = build_grounded_policy_response(
            "What is data retention?",
            chunks,
            retrieval_confidence=0.82,
            low_confidence=False,
        )

        self.assertIn(
            "privacy.pdf",
            response,
        )
        mock_llm.invoke.assert_called_once()

    @patch("backend.llm.llm")
    def test_unsupported_policy_without_chunks(
        self,
        mock_llm,
    ):

        from services.policy_response_service import (
            LOW_CONFIDENCE_MESSAGE,
            build_grounded_policy_response,
        )

        response = build_grounded_policy_response(
            "Describe the intergalactic hiring statute",
            chunks=[],
            retrieval_confidence=0.1,
            low_confidence=True,
        )

        self.assertEqual(
            response,
            LOW_CONFIDENCE_MESSAGE,
        )
        mock_llm.invoke.assert_not_called()


if __name__ == "__main__":

    unittest.main()
