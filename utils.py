from os.path import exists

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
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


def remove_characters(text: str, wordlist: list[str], replace_with: str = "") -> str:
    for word in wordlist:
        text = "{}".format(replace_with).join(text.split(word))
    return text


def break_text(text: str, max_length: int = 120):
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > max_length:
            lines.append(line.strip())
            line = word
        else:
            line += " " + word
    lines.append(line.strip())
    return "\n".join(lines)


def url_download_document(url: str) -> Document | None:
    # we expect the document might not be a pdf from PyPDFLoader
    # and expect that the site might block us from WebBaseLoader
    # note: both PDF loader, and web loader output a lot of useless warnings to the terminal
    try:
        document = PyPDFLoader(url).load()
    except Exception:
        try:
            document = WebBaseLoader(url).load()
        except Exception as e:
            print("error downloading:", e)
            return None

    retrieved_doc = document[0]

    text = document[0].page_content
    text = remove_characters(text, ["\n"])
    text = break_text(text)

    retrieved_doc.page_content = text

    return retrieved_doc
