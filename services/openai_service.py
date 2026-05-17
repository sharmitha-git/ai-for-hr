import os

from openai import OpenAI

from dotenv import load_dotenv


load_dotenv()


client = OpenAI(

    api_key=os.getenv(
        "OPENAI_API_KEY"
    ),

    base_url=os.getenv(
        "OPENAI_BASE_URL"
    )
)


class OpenAIService:


    @staticmethod
    def generate_embedding(
        text: str
    ):
        print("Generating embedding ...")
        response = client.embeddings.create(

            model="text-embedding-3-small",

            input=text
        )

        return response.data[0].embedding