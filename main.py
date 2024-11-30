# compare search methods:
# - algolia API search (likely hybrid search)
# - trivial ctrl-f search (keyword search)
# - what can be actually seen in the story (purely vector search)
# try doing this in one file, that should make it much easier to read through for presentation's sake
import math

import faiss
from langchain_community.docstore import InMemoryDocstore
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api import get_stories, HNPathsV0
from utils import is_text_junk

# -=-=-=-

# Introduction to embeddings - the overlooked common uses of LMs other than text/video/audio genAi

# A simple embedding workflow for semantic querying through HackerNews API

# -=-=-=-


retrieved_stories = get_stories(type_url=HNPathsV0.TOP_STORIES, max_amount=10)

# init embedder

model = "mxbai-embed-large:latest"

embedder = OllamaEmbeddings(model=model, base_url="http://localhost:11434")

# index has to know how many dimensions it'll be storing

embedding_dimensions = len(embedder.embed_query("anything"))

# in FAISS, index controls how the data is structured, how it's de-duplicated, and how it's searched

index_type = faiss.IndexFlatL2(embedding_dimensions)

# init vector db

vector_db = FAISS(
    embedding_function=embedder,
    index=index_type,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

# init text splitter

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n\n", "\n\n", "\n", ". ", ", ", " ", ""],
    chunk_size=1024,  # HN articles tend to be short, better to capture them in their entirety
    chunk_overlap=math.ceil(1024 / 3),  # 30% overlap
    keep_separator=False,
    strip_whitespace=True,
)

# embed all the stories

for story in retrieved_stories:
    if story.text is None:
        # story's URL likely 404'd
        print("story unavailable:", story.title)
        continue

    # split each story into multiple, easy to embed chunks

    text_chunks = text_splitter.split_text(story.text)
    document_chunks = []

    for chunk in text_chunks:
        if is_text_junk(chunk):
            text_chunks.remove(chunk)
            continue

        # convert the text to a Document to add metadata
        document_chunk = Document(page_content=chunk)
        document_chunk.metadata = story.document.metadata
        document_chunk.metadata["hn_title"] = story.title
        document_chunks.append(document_chunk)

    if len(document_chunks) != 0:
        vector_db.add_documents(documents=document_chunks, embeddings=embedder)
        print("story indexed:", story.title)

# query through the embeddings

while True:
    query = input("query: ")
    result = vector_db.similarity_search(query=query, k=1)[0]
    print(
        "result most closely matching the query: \n",
        result.page_content,
        "\ntitle:",
        result.metadata.get("hn_title"),
        "\nsource:",
        result.metadata.get("source"),
    )
