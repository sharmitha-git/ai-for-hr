from repositories.application_repository import (
    ApplicationRepository
)
from repositories.candidate_repository import (
    CandidateRepository
)
from repositories.feedback_repository import (
    FeedbackRepository
)
from repositories.job_repository import (
    JobRepository
)
from services.policy_rag_service import (
    search_policy_documents
)


class DecisionSupportService:


    @staticmethod
    def _normalize_skills(skills_text):

        if not skills_text:

            return set()

        return {
            skill.strip().lower()
            for skill in skills_text.split(",")
            if skill.strip()
        }


    @staticmethod
    def _summarize_feedback(feedback_rows):

        if not feedback_rows:

            return {
                "count": 0,
                "latest_action": None,
                "latest_notes": None
            }

        latest = feedback_rows[0]

        return {
            "count": len(feedback_rows),
            "latest_action": latest.get(
                "recruiter_action"
            ),
            "latest_notes": latest.get(
                "recruiter_notes"
            )
        }


    @staticmethod
    def build_application_packet(
        application_id
    ):

        application = (
            ApplicationRepository
            .get_application_by_id(
                application_id
            )
        )

        if not application:

            return None

        candidate = (
            CandidateRepository
            .get_candidate_by_id(
                application["candidate_id"]
            )
        )

        job = (
            JobRepository
            .get_job_by_id(
                application["job_id"]
            )
        )

        feedback_rows = (
            FeedbackRepository
            .get_feedback_for_application(
                application_id
            )
        )

        required_skills = (
            DecisionSupportService
            ._normalize_skills(
                job.get(
                    "required_skills",
                    ""
                )
            )
            if job else set()
        )

        candidate_skills = (
            DecisionSupportService
            ._normalize_skills(
                candidate.get(
                    "skills",
                    ""
                )
            )
            if candidate else set()
        )

        matched_skills = sorted(
            required_skills.intersection(
                candidate_skills
            )
        )

        missing_skills = sorted(
            required_skills.difference(
                candidate_skills
            )
        )

        governance_status = application.get(
            "governance_flag"
        ) or "REVIEW"

        if governance_status == "SAFE":

            recommendation = (
                "Recommend recruiter review for "
                "possible shortlist."
            )

        elif governance_status == "REVIEW":

            recommendation = (
                "Recommend manual recruiter review "
                "before any next step."
            )

        else:

            recommendation = (
                "Recommend escalation to human review; "
                "do not reject automatically."
            )

        policy_query = (
            f"Hiring review policy for {job['title']}"
            if job and job.get("title")
            else "Hiring review policy human approval"
        )

        policy_payload = search_policy_documents(
            policy_query
        )
        policy_evidence = (
            policy_payload.get("results", [])
            if isinstance(policy_payload, dict)
            else policy_payload
        )

        risks = []

        if missing_skills:

            risks.append(
                "Candidate is missing some required skills."
            )

        if governance_status != "SAFE":

            risks.append(
                "Governance status requires manual review."
            )

        if not feedback_rows:

            risks.append(
                "No recruiter feedback recorded yet."
            )

        return {
            "application": application,
            "candidate": candidate,
            "job": job,
            "feedback_summary": (
                DecisionSupportService
                ._summarize_feedback(
                    feedback_rows
                )
            ),
            "feedback_history": feedback_rows,
            "explainability": {
                "semantic_score":
                    application.get(
                        "semantic_score"
                    ),
                "keyword_score":
                    application.get(
                        "keyword_score"
                    ),
                "final_score":
                    application.get(
                        "final_score"
                    ),
                "confidence_score":
                    application.get(
                        "confidence_score"
                    ),
                "matched_skills":
                    matched_skills,
                "missing_skills":
                    missing_skills
            },
            "policy_evidence":
                policy_evidence,
            "recommendation":
                recommendation,
            "risks":
                risks,
            "human_action_required":
                True,
            "allowed_actions": [
                "REQUEST_INTERVIEW",
                "ASK_FOR_MORE_INFO",
                "SHORTLIST_AFTER_HUMAN_APPROVAL",
                "REJECT_AFTER_HUMAN_APPROVAL"
            ],
            "decision_boundary": (
                "AI can assist with scoring and "
                "explanations, but a human reviewer "
                "must approve any shortlist or reject "
                "decision."
            )
        }
