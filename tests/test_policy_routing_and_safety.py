"""
Evaluation tests for policy routing, safety refusals, and grounded responses.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


from backend.routing.copilot_router import (
    RECRUITER_AGENTS,
    build_route_plan,
    classify_query_intent,
    is_policy_compliance_query,
)
from services.policy_safety_service import (
    check_query_safety,
)


class PolicyRoutingTests(unittest.TestCase):

    def _assert_policy_route(self, query):

        plan = build_route_plan(query)

        self.assertEqual(
            plan["selected_agent"],
            "policy",
        )
        self.assertEqual(
            plan["route_type"],
            "policy_compliance",
        )
        self.assertNotIn(
            plan["selected_agent"],
            RECRUITER_AGENTS,
        )
        self.assertTrue(
            plan.get(
                "routing_metadata",
                {},
            ).get(
                "force_policy_route"
            )
        )

    def test_sensitive_data_protected_routes_to_policy(self):

        self._assert_policy_route(
            "does sensitive data are protected"
        )

    def test_is_sensitive_data_protected(self):

        self._assert_policy_route(
            "is sensitive data protected"
        )

    def test_gdpr_policy_routes_to_policy(self):

        self._assert_policy_route(
            "what is GDPR policy"
        )

    def test_candidate_data_storage_routes_to_policy(self):

        self._assert_policy_route(
            "how is candidate data stored"
        )

    def test_governance_rules_routes_to_policy(self):

        self._assert_policy_route(
            "show governance rules"
        )

    def test_privacy_query_routes_to_policy_agent(self):

        self._assert_policy_route(
            "What is our privacy policy for candidate data?"
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

    def test_routing_metadata_logged_fields(self):

        plan = build_route_plan(
            "is sensitive data protected"
        )
        metadata = plan["routing_metadata"]

        self.assertEqual(
            metadata["detected_intent"],
            "policy_compliance",
        )
        self.assertGreater(
            metadata["confidence"],
            0.5,
        )
        self.assertTrue(
            len(metadata["matched_signals"]) > 0
        )

    def test_policy_intent_blocks_recruiter_default(self):

        classification = classify_query_intent(
            "does sensitive data are protected"
        )

        self.assertTrue(
            classification["force_policy_route"]
        )
        self.assertEqual(
            classification["detected_intent"],
            "policy_compliance",
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

    def test_low_confidence_returns_no_grounded_message(self):

        from services.policy_response_service import (
            NO_GROUNDED_POLICY_MESSAGE,
            build_grounded_policy_response,
        )

        response = build_grounded_policy_response(
            "What is the moonlighting policy?",
            chunks=[],
            retrieval_confidence=0.0,
            low_confidence=True,
        )

        self.assertEqual(
            response,
            NO_GROUNDED_POLICY_MESSAGE,
        )
        self.assertIn(
            "No grounded policy information found",
            response,
        )

    @patch("backend.llm.llm")
    def test_unsupported_policy_without_chunks(
        self,
        mock_llm,
    ):

        from services.policy_response_service import (
            NO_GROUNDED_POLICY_MESSAGE,
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
            NO_GROUNDED_POLICY_MESSAGE,
        )
        mock_llm.invoke.assert_not_called()


if __name__ == "__main__":

    unittest.main()
