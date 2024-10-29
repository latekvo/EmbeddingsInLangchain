from os.path import exists

from langchain_community.vectorstores.faiss import FAISS
from langchain_core.embeddings import Embeddings

EMBEDDER_NAME = "placeholder_embedding_model_name"
VECTOR_DB_NAME = "embeddings"


def create_faiss_db_if_not_exists(
    db_name: str, folder_path: str, embeddings: Embeddings
):
    if not exists(folder_path + "/" + db_name + ".faiss"):
        vector_store = FAISS.from_texts(
            ["You are a large language model, intended for research purposes."],
            embeddings,
        )
        vector_store.save_local(folder_path=folder_path, index_name=db_name)
    else:
        print("Vector database already exists:", db_name + ".faiss")
