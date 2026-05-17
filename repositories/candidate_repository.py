from sqlalchemy import text

from database.connection import (
    engine
)


class CandidateRepository:


    @staticmethod
    def create_candidate(

        full_name,
        email,
        phone,
        resume_filename,
        original_resume,
        masked_resume,
        skills
    ):

        query = text("""

            INSERT INTO candidates (

                full_name,
                email,
                phone,
                resume_filename,
                original_resume,
                masked_resume,
                skills

            )

            VALUES (

                :full_name,
                :email,
                :phone,
                :resume_filename,
                :original_resume,
                :masked_resume,
                :skills

            )

            RETURNING id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "resume_filename": resume_filename,
                    "original_resume": original_resume,
                    "masked_resume": masked_resume,
                    "skills": skills
                }
            )

            conn.commit()

            return result.fetchone()[0]


    @staticmethod
    def get_all_candidates():

        query = text("""

            SELECT * FROM candidates
            ORDER BY created_at DESC

        """)

        with engine.connect() as conn:

            result = conn.execute(query)

            return [
                dict(row._mapping)
                for row in result
            ]
        
    @staticmethod
    def get_candidate_by_id(
        candidate_id
    ):

        query = text("""

            SELECT * FROM candidates
            WHERE id = :candidate_id

        """)

        with engine.connect() as conn:

            result = conn.execute(

                query,

                {
                    "candidate_id": candidate_id
                }
            )

            row = result.fetchone()

            if row:

                return dict(row._mapping)

            return None