from sqlalchemy import text

from database.connection import (
    engine
)


class JobRepository:


    @staticmethod
    def create_job(

        title,
        description,
        required_skills
    ):

        query = text("""

            INSERT INTO jobs (

                title,
                description,
                required_skills

            )

            VALUES (

                :title,
                :description,
                :required_skills

            )

            RETURNING id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "title": title,
                    "description": description,
                    "required_skills": required_skills
                }
            )

            conn.commit()

            return result.fetchone()[0]


    @staticmethod
    def get_all_jobs():

        query = text("""

            SELECT * FROM jobs
            ORDER BY created_at DESC

        """)

        with engine.connect() as conn:

            result = conn.execute(query)

            return [
                dict(row._mapping)
                for row in result
            ]
        
    @staticmethod
    def get_job_by_id(
        job_id
    ):

        query = text("""

            SELECT * FROM jobs
            WHERE id = :job_id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "job_id": job_id
                }
            )

            row = result.fetchone()

            if row:

                return dict(row._mapping)

            return None