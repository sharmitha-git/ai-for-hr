from sqlalchemy import text

from database.connection import (
    SessionLocal
)


class FeedbackRepository:


    @staticmethod
    def create_feedback(

        application_id,
        recruiter_action,
        recruiter_notes
    ):

        db = SessionLocal()

        try:

            result = db.execute(

                text(
                    """
                    INSERT INTO recruiter_feedback (

                        application_id,

                        recruiter_action,

                        recruiter_notes

                    )

                    VALUES (

                        :application_id,

                        :recruiter_action,

                        :recruiter_notes
                    )

                    RETURNING id
                    """
                ),

                {

                    "application_id":
                        application_id,

                    "recruiter_action":
                        recruiter_action,

                    "recruiter_notes":
                        recruiter_notes
                }
            )

            db.commit()

            feedback_id = (
                result.fetchone()[0]
            )

            return feedback_id

        finally:

            db.close()

    @staticmethod
    def get_feedback_for_application(
        application_id
    ):

        db = SessionLocal()

        try:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM recruiter_feedback
                    WHERE application_id = :application_id
                    ORDER BY created_at DESC
                    """
                ),

                {
                    "application_id":
                        application_id
                }
            )

            return [
                dict(row._mapping)
                for row in result
            ]

        finally:

            db.close()
