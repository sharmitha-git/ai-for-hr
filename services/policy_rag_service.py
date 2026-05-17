from langchain_community.document_loaders import (
    PyPDFLoader
)

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)

from langchain_openai import (
    OpenAIEmbeddings
)

from langchain_community.vectorstores import (
    Chroma
)

import os


POLICY_DB_PATH = (
    "memory/policy_chroma"
)


def ingest_policy_documents():

    documents = []

    policy_folder = (
        "data/policies"
    )

    if not os.path.isdir(
        policy_folder
    ):

        return 0

    for file in os.listdir(
        policy_folder
    ):

        if file.endswith(".pdf"):

            loader = PyPDFLoader(

                os.path.join(
                    policy_folder,
                    file
                )
            )

            docs = loader.load()

            documents.extend(docs)

    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(

        chunks,

        embedding=embeddings,

        persist_directory=
            POLICY_DB_PATH
    )

    vectordb.persist()

    return len(chunks)


def search_policy_documents(query):

    if not os.path.isdir(
        POLICY_DB_PATH
    ):

        return []

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma(

        persist_directory=
            POLICY_DB_PATH,

        embedding_function=
            embeddings
    )

    try:

        docs = vectordb.similarity_search(

            query,

            k=3
        )

    except Exception:

        return []

    return [

        d.page_content

        for d in docs
    ]
