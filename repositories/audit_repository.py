from sqlalchemy import text

from database.connection import (
    engine
)


class AuditRepository:


    @staticmethod
    def create_log(

        application_id,

        action_type,

        action_details
    ):

        query = text("""

            INSERT INTO audit_logs (

                application_id,

                action_type,

                action_details

            )

            VALUES (

                :application_id,

                :action_type,

                :action_details
            )

        """)

        with engine.connect() as conn:

            conn.execute(

                query,

                {

                    "application_id":
                        application_id,

                    "action_type":
                        action_type,

                    "action_details":
                        action_details
                }
            )

            conn.commit()
    
    @staticmethod
    def get_all_logs():

        query = text("""

            SELECT *

            FROM audit_logs

            ORDER BY created_at DESC

        """)

        with engine.connect() as conn:

            result = conn.execute(query)

            return [

                dict(row._mapping)

                for row in result
            ]