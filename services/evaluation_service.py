import numpy as np

from repositories.job_repository import (
    JobRepository
)

from repositories.application_repository import (
    ApplicationRepository
)

from repositories.candidate_repository import (
    CandidateRepository
)

from services.openai_service import (
    OpenAIService
)

from services.chroma_service import (
    ChromaService
)
from repositories.audit_repository import (
    AuditRepository
)
from services.decision_support_service import (
    DecisionSupportService
)


class EvaluationService:


    # =====================================
    # Cosine Similarity
    # =====================================

    @staticmethod
    def cosine_similarity(
        a,
        b
    ):

        a = np.array(a)

        b = np.array(b)

        return np.dot(a, b) / (
            np.linalg.norm(a)
            *
            np.linalg.norm(b)
        )


    # =====================================
    # Keyword Overlap
    # =====================================

    @staticmethod
    def keyword_score(

        jd_skills,
        candidate_skills
    ):

        jd_set = set(

            skill.strip().lower()

            for skill in jd_skills.split(",")
        )

        candidate_set = set(

            skill.strip().lower()

            for skill in candidate_skills.split(",")
        )

        overlap = jd_set.intersection(
            candidate_set
        )

        return (
            len(overlap)
            /
            max(len(jd_set), 1)
        ) * 100


    # =====================================
    # Governance Logic
    # =====================================

    @staticmethod
    def governance_decision(

        semantic_score,
        keyword_score
    ):

        if (
            semantic_score >= 65
            and keyword_score >= 60
        ):

            return (
                "SAFE",
                "Strong Match"
            )

        elif (
            semantic_score >= 45
            and keyword_score >= 30
        ):

            return (
                "REVIEW",
                "Needs Recruiter Review"
            )

        return (
            "ESCALATE",
            "Potential mismatch. Human review required."
        )


    # =====================================
    # Evaluate Job Applications
    # =====================================

    @staticmethod
    def evaluate_job(
        job_id
    ):

        # -----------------------------
        # Fetch Job
        # -----------------------------

        job = JobRepository.get_job_by_id(
            job_id
        )

        if not job:

            return []

        jd_text = (
            job["description"]
            +
            "\n"
            +
            job["required_skills"]
        )

        # -----------------------------
        # Generate Job Embedding
        # -----------------------------

        job_embedding = (
            OpenAIService.generate_embedding(
                jd_text
            )
        )

        # -----------------------------
        # Store Job Embedding
        # -----------------------------

        ChromaService.store_job_embedding(

            job_id=job_id,

            embedding=job_embedding,

            metadata={

                "job_id": job_id,

                "title": job["title"]
            }
        )

        # -----------------------------
        # Fetch Applications
        # -----------------------------

        applications = (

            ApplicationRepository
            .get_applications_by_job(
                job_id
            )
        )

        # -----------------------------
        # Fetch Candidate Embeddings
        # -----------------------------

        candidate_vectors = (
            ChromaService
            .get_all_candidate_embeddings()
        )

        results = []

        # -----------------------------
        # Evaluate Each Application
        # -----------------------------

        for application in applications:

            candidate_id = (
                application[
                    "candidate_id"
                ]
            )

            candidate = (
                CandidateRepository
                .get_candidate_by_id(
                    candidate_id
                )
            )

            if not candidate:

                continue

            # -------------------------
            # Find Candidate Embedding
            # -------------------------

            candidate_embedding = None

            for i, metadata in enumerate(

                candidate_vectors[
                    "metadatas"
                ]
            ):

                if (

                    metadata[
                        "candidate_id"
                    ]

                    ==

                    candidate_id
                ):

                    candidate_embedding = (

                        candidate_vectors[
                            "embeddings"
                        ][i]
                    )

                    break

            if candidate_embedding is None:

                continue

            # -------------------------
            # Semantic Score
            # -------------------------

            semantic_score = float(

                EvaluationService
                .cosine_similarity(

                    job_embedding,
                    candidate_embedding
                )

                * 100
            )

            # -------------------------
            # Keyword Score
            # -------------------------

            keyword_score = (

                EvaluationService
                .keyword_score(

                    job[
                        "required_skills"
                    ],

                    candidate[
                        "skills"
                    ]
                )
            )

            # -------------------------
            # Final Score
            # -------------------------

            final_score = float(

                semantic_score * 0.7
                +
                keyword_score * 0.3
            )
            # -------------------------
            # Confidence Score
            # -------------------------

            confidence_score = round(

                (
                    semantic_score * 0.5
                    +
                    keyword_score * 0.5
                ),

                2
            )
            # -------------------------
            # Governance Logic
            # -------------------------

            governance_status, explanation = (

                EvaluationService
                .governance_decision(

                    semantic_score,
                    keyword_score
                )
            )

            # -------------------------
            # Persist Scores
            # -------------------------

            ApplicationRepository.update_scores(

                application_id=
                    application["id"],

                semantic_score=round(
                    semantic_score,
                    2
                ),

                keyword_score=round(
                    keyword_score,
                    2
                ),

                final_score=round(
                    final_score,
                    2
                ),
                confidence_score=confidence_score,
        

                governance_flag=
                    governance_status
            )
            AuditRepository.create_log(

                application_id=
                    application["id"],

                action_type=
                    "EVALUATION_COMPLETED",

                action_details=(

                    f"Candidate scored "
                    f"{round(final_score,2)} "
                    f"with governance status "
                    f"{governance_status}"
                )
            )
            application = ApplicationRepository.get_application(candidate_id, job_id)
            support_packet = (
                DecisionSupportService
                .build_application_packet(
                    application["id"]
                )
            )
            # -------------------------
            # Build Response
            # -------------------------

            results.append({

                "application_id":
                    application["id"],

                "candidate_id":
                    candidate_id,

                "candidate_name":
                    candidate[
                        "full_name"
                    ],

                "semantic_score": round(
                    semantic_score,
                    2
                ),

                "keyword_score": round(
                    keyword_score,
                    2
                ),

                "final_score": round(
                    final_score,
                    2
                ),

                "governance_status":
                    governance_status,
                "confidence_score":
                    confidence_score,
                "application_status":
                    application[
                    "application_status"
                ],
                "human_action_required":
                    True,
                "explanation":
                    (
                        f"{explanation}. "
                        f"This score is advisory only "
                        f"and cannot shortlist or reject "
                        f"a candidate without a human reviewer."
                    ),
                "explainability": {

                    "semantic_weight":
                        "70% semantic similarity",

                    "keyword_weight":
                        "30% keyword overlap",

                    "matched_skills":

                        support_packet[
                            "explainability"
                        ][
                            "matched_skills"
                        ],
                    "missing_skills":
                        support_packet[
                            "explainability"
                        ][
                            "missing_skills"
                        ]
                },
                "feedback_summary":
                    support_packet[
                        "feedback_summary"
                    ],
                "policy_evidence":
                    support_packet[
                        "policy_evidence"
                    ],
                "recommendation":
                    support_packet[
                        "recommendation"
                    ],
                "decision_boundary":
                    support_packet[
                        "decision_boundary"
                    ]
            })

        # -----------------------------
        # Sort Results
        # -----------------------------

        results.sort(

            key=lambda x: x[
                "final_score"
            ],

            reverse=True
        )

        return results
