from sqlalchemy import text

from database.connection import (
    engine
)


class ApplicationRepository:


    # =====================================
    # Create Application
    # =====================================

    @staticmethod
    def create_application(

        candidate_id,
        job_id,
        application_status="PENDING"
    ):

        query = text("""

            INSERT INTO applications (

                candidate_id,
                job_id,
                application_status

            )

            VALUES (

                :candidate_id,
                :job_id,
                :application_status

            )

            RETURNING id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {

                    "candidate_id":
                        candidate_id,

                    "job_id":
                        job_id,

                    "application_status":
                        application_status
                }
            )

            conn.commit()

            return result.fetchone()[0]


    # =====================================
    # Get All Applications
    # =====================================

    @staticmethod
    def get_all_applications():

        query = text("""

            SELECT * FROM applications
            ORDER BY created_at DESC

        """)

        with engine.connect() as conn:

            result = conn.execute(query)

            return [

                dict(row._mapping)

                for row in result
            ]


    # =====================================
    # Get Applications By Job
    # =====================================

    @staticmethod
    def get_applications_by_job(
        job_id
    ):

        query = text("""

            SELECT *

            FROM applications

            WHERE job_id = :job_id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "job_id": job_id
                }
            )

            return [

                dict(row._mapping)

                for row in result
            ]


    # =====================================
    # Get Single Application
    # =====================================

    @staticmethod
    def get_application(

        candidate_id,
        job_id
    ):

        query = text("""

            SELECT *

            FROM applications

            WHERE candidate_id = :candidate_id
            AND job_id = :job_id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {

                    "candidate_id":
                        candidate_id,

                    "job_id":
                        job_id
                }
            )

            row = result.fetchone()

            if row:

                return dict(row._mapping)

            return None

    @staticmethod
    def get_application_by_id(
        application_id
    ):

        query = text("""

            SELECT *

            FROM applications

            WHERE id = :application_id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "application_id":
                        application_id
                }
            )

            row = result.fetchone()

            if row:

                return dict(row._mapping)

            return None


    # =====================================
    # Update Scores
    # =====================================

    @staticmethod
    def update_scores(

        application_id,

        semantic_score,

        keyword_score,

        final_score,
        
        confidence_score,

        governance_flag
    ):

        query = text("""

            UPDATE applications

            SET

                semantic_score = :semantic_score,

                keyword_score = :keyword_score,

                final_score = :final_score,

                confidence_score = :confidence_score,

                governance_flag = :governance_flag

            WHERE id = :application_id

        """)

        with engine.connect() as conn:

            conn.execute(

                query,

                {

                    "semantic_score":
                        semantic_score,

                    "keyword_score":
                        keyword_score,

                    "final_score":
                        final_score,

                    "confidence_score":
                        confidence_score,

                    "governance_flag":
                        governance_flag,

                    "application_id":
                        application_id
                }
            )

            conn.commit()


    # =====================================
    # Update Application Status
    # =====================================

    @staticmethod
    def update_application_status(

        application_id,

        application_status
    ):

        query = text("""

            UPDATE applications

            SET

                application_status =
                    :application_status

            WHERE id = :application_id

        """)

        with engine.connect() as conn:

            conn.execute(

                query,

                {

                    "application_status":
                        application_status,

                    "application_id":
                        application_id
                }
            )

            conn.commit()
