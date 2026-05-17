from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

import numpy as np

from repositories.candidate_repository import (
    CandidateRepository
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def semantic_candidate_search(query):

    candidates = (
        CandidateRepository
        .get_all_candidates()
    )

    query_embedding = (
        model.encode(query)
    )

    ranked_candidates = []

    for candidate in candidates:

        resume_text = (
            candidate["original_resume"]
        )

        resume_embedding = (
            model.encode(resume_text)
        )

        similarity = cosine_similarity(

            [query_embedding],

            [resume_embedding]

        )[0][0]

        candidate["search_score"] = round(
            float(similarity),
            4
        )

        ranked_candidates.append(
            candidate
        )

    ranked_candidates = sorted(

        ranked_candidates,

        key=lambda x: x["search_score"],

        reverse=True
    )

    return ranked_candidates[:5]