import os
from uuid import uuid4

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from repositories.candidate_repository import (
    CandidateRepository
)

from repositories.job_repository import (
    JobRepository
)

from repositories.application_repository import (
    ApplicationRepository
)

from services.resume_parser import (
    ResumeParser
)

from services.privacy_service import (
    PrivacyService
)

from services.openai_service import (
    OpenAIService
)

from services.chroma_service import (
    ChromaService,
    candidate_collection
)
from services.evaluation_service import (
    EvaluationService
)
from services.decision_support_service import (
    DecisionSupportService
)
from repositories.feedback_repository import (
    FeedbackRepository
)
from repositories.audit_repository import (
    AuditRepository
)
from backend.models import (
    ApplicationStatusUpdate,
    CopilotRequest
)

from backend.graphs.hiring_graph import (
    hiring_graph
)

router = APIRouter()


os.makedirs(
    "data/resumes",
    exist_ok=True
)


# =========================================
# Upload Candidate
# =========================================

@router.post("/upload-candidate")
async def upload_candidate(

    full_name: str = Form(...),

    email: str = Form(...),

    phone: str = Form(...),

    skills: str = Form(...),

    job_id: int = Form(...),

    file: UploadFile = File(...)
):

    save_path = (
        f"data/resumes/{file.filename}"
    )

    with open(save_path, "wb") as buffer:

        buffer.write(
            await file.read()
        )

    # -----------------------------
    # Parse Resume
    # -----------------------------

    original_resume = (
        ResumeParser.parse_pdf(
            save_path
        )
    )

    # -----------------------------
    # PII Masking
    # -----------------------------

    privacy_output = (
        PrivacyService.mask_pii(
            original_resume
        )
    )

    print(
        "PII masking completed"
    )

    # -----------------------------
    # Embedding Generation
    # -----------------------------

    embedding = (
        OpenAIService.generate_embedding(

            privacy_output[
                "masked_text"
            ]
        )
    )

    print(
        "Embedding generated"
    )

    # -----------------------------
    # Store Candidate
    # -----------------------------

    candidate_id = (
        CandidateRepository.create_candidate(

            full_name=full_name,

            email=email,

            phone=phone,

            resume_filename=file.filename,

            original_resume=original_resume,

            masked_resume=privacy_output[
                "masked_text"
            ],

            skills=skills
        )
    )

    # -----------------------------
    # Store Vector
    # -----------------------------

    ChromaService.store_candidate_embedding(

        candidate_id=candidate_id,

        embedding=embedding,

        metadata={

            "candidate_id": candidate_id,

            "name": full_name,

            "skills": skills
        }
    )

    print(
        "Vector stored"
    )

    # -----------------------------
    # Create Application
    # -----------------------------

    application_id = (
        ApplicationRepository
        .create_application(

            candidate_id=candidate_id,

            job_id=job_id
        )
    )

    # -----------------------------
    # Response
    # -----------------------------

    return {

        "candidate_id": candidate_id,

        "application_id": application_id,

        "message": (
            "Candidate uploaded successfully"
        ),

        "masked_preview": privacy_output[
            "masked_text"
        ][:500]
    }


# =========================================
# Create Job
# =========================================

@router.post("/create-job")
async def create_job(

    title: str = Form(...),

    description: str = Form(...),

    required_skills: str = Form(...)
):

    job_id = JobRepository.create_job(

        title=title,

        description=description,

        required_skills=required_skills
    )

    return {

        "job_id": job_id,

        "message": (
            "Job created successfully"
        )
    }


# =========================================
# Get Jobs
# =========================================

@router.get("/jobs")
async def get_jobs():

    jobs = (
        JobRepository.get_all_jobs()
    )

    return jobs


# =========================================
# Debug Chroma
# =========================================

@router.get("/debug-chroma")
async def debug_chroma():

    data = candidate_collection.get()

    return {

        "total_vectors": len(
            data["ids"]
        ),

        "ids": data["ids"],

        "metadatas": data[
            "metadatas"
        ]
    }
# =========================================
# Evaluate Job
# =========================================

@router.get("/evaluate-job/{job_id}")
async def evaluate_job(
    job_id: int
):

    results = (
        EvaluationService
        .evaluate_job(job_id)
    )

    return results

# =========================================
# Feedback from Recruiter
# =========================================

@router.post("/recruiter-feedback")
async def recruiter_feedback(

    application_id: int = Form(...),

    recruiter_action: str = Form(...),

    recruiter_notes: str = Form(...)
):

    feedback_id = (

        FeedbackRepository
        .create_feedback(

            application_id,

            recruiter_action,

            recruiter_notes
        )
    )

    AuditRepository.create_log(

        application_id=application_id,

        action_type="RECRUITER_FEEDBACK_CAPTURED",

        action_details=(
            f"Recruiter action={recruiter_action}; "
            f"notes={recruiter_notes}"
        )
    )

    return {

        "feedback_id": feedback_id,

        "message": (
            "Recruiter feedback stored"
        )
    }

# =========================================
# Update Application Status
# =========================================

@router.put("/update-application-status")
async def update_application_status(

    payload: ApplicationStatusUpdate
):

    existing_application = (
        ApplicationRepository
        .get_application_by_id(
            payload.application_id
        )
    )

    if not existing_application:

        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    normalized_status = (
        payload.application_status
        .strip()
        .upper()
    )

    allowed_statuses = {
        "PENDING",
        "UNDER_REVIEW",
        "SHORTLISTED",
        "REJECTED"
    }

    if normalized_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Unsupported application status"
        )

    ApplicationRepository.update_application_status(

        application_id=payload.application_id,

        application_status=normalized_status
    )

    reviewer_name = (
        payload.reviewer_name
        or "human_reviewer"
    )

    reviewer_notes = (
        payload.reviewer_notes
        or "No reviewer notes provided."
    )

    AuditRepository.create_log(

        application_id=payload.application_id,

        action_type="HUMAN_STATUS_UPDATED",

        action_details=(
            f"reviewer={reviewer_name}; "
            f"status={normalized_status}; "
            f"notes={reviewer_notes}; "
            f"previous_status="
            f"{existing_application.get('application_status')}"
        )
    )

    return {

        "message":
            "Application status updated with human approval",

        "application_id":
            payload.application_id,

        "application_status":
            normalized_status,

        "reviewer_name":
            reviewer_name,

        "human_in_the_loop":
            True
    }

# =========================================
# Audit Logs
# =========================================

@router.get("/audit-logs")
async def get_audit_logs():

    logs = (
        AuditRepository
        .get_all_logs()
    )

    return logs


@router.get("/applications")
async def get_applications():

    applications = (
        ApplicationRepository
        .get_all_applications()
    )

    return applications


@router.get(
    "/application-feedback/{application_id}"
)
async def get_application_feedback(
    application_id: int
):

    return (
        FeedbackRepository
        .get_feedback_for_application(
            application_id
        )
    )


@router.get(
    "/candidate/{candidate_id}"
)
async def get_candidate(
    candidate_id: int
):

    candidate = (
        CandidateRepository
        .get_candidate_by_id(
            candidate_id
        )
    )

    return candidate


@router.get(
    "/decision-support/{application_id}"
)
async def decision_support(
    application_id: int
):

    packet = (
        DecisionSupportService
        .build_application_packet(
            application_id
        )
    )

    if not packet:

        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return packet

@router.post("/copilot")
async def copilot_route(

    payload: CopilotRequest
):

    trace_id = str(
        uuid4()
    )

    AuditRepository.create_log(

        application_id=None,

        action_type="COPILOT_QUERY_RECEIVED",

        action_details=(
            f"trace_id={trace_id}; "
            f"query={payload.query}"
        )
    )

    result = hiring_graph.invoke({

        "query":
            payload.query,
        "session_id": "default_user",
        "trace_id": trace_id
    })

    AuditRepository.create_log(

        application_id=None,

        action_type="COPILOT_QUERY_COMPLETED",

        action_details=(
            f"trace_id={trace_id}; "
            f"selected_agent="
            f"{result.get('selected_agent')}"
        )
    )

    result["trace_id"] = trace_id
    result["human_in_the_loop"] = True

    return result
