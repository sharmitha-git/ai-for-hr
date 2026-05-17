from repositories.candidate_repository import (
    CandidateRepository
)

from repositories.application_repository import (
    ApplicationRepository
)

from repositories.audit_repository import (
    AuditRepository
)


def get_candidates():

    return (
        CandidateRepository
        .get_all_candidates()
    )


def get_applications():

    return (
        ApplicationRepository
        .get_all_applications()
    )


def get_audit_logs():

    return (
        AuditRepository
        .get_all_logs()
    )