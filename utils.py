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


def is_text_junk(text: str):
    # checks if text contains any of junky keywords eg: privacy policy, subscribe, cookies etc.
    # do not expand this list, it has to be small to be efficient, and these words are grouped either way.
    trigger_list = [
        "sign in",
        "privacy policy",
        "skip to",
        "newsletter",
        "subscribe",
        "related tags",
        "share price",
    ]
    low_text = text.lower()
    for trigger in trigger_list:
        if trigger in low_text:
            return True
    return False
