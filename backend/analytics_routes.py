from fastapi import APIRouter

from services.analytics_service import (
    AnalyticsService
)


router = APIRouter(
    tags=["analytics"]
)


@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    start_date: str | None = None,
    end_date: str | None = None,
    job_id: int | None = None,
):

    return AnalyticsService.get_dashboard(
        start_date=start_date,
        end_date=end_date,
        job_id=job_id,
    )


@router.get("/analytics/export")
async def get_analytics_export(
    start_date: str | None = None,
    end_date: str | None = None,
    job_id: int | None = None,
):

    return AnalyticsService.get_export_dataset(
        start_date=start_date,
        end_date=end_date,
        job_id=job_id,
    )
