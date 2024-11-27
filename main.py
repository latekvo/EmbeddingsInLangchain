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

# introduction, overlooked common uses of generative LLMs, for purposes other than text/video/audio generation

# introduction to embeddings

# "so, let's say we wanted to search through a large data store"

# as the data source, we'll use articles coming from the HackNews API
# [separate file as that's not the focus]

# trivial search
# [separate file as that's not the focus]

# "now here's how embeddings come into play"

# we need an embedding model
# showcase how any model can be used for this
# present the technical principal for this happening, how LLM architectures look,
# how we can extract the last non-decoder layer as the abstract multi-dimensional object

# showcase how we're better off using the faster models, use a faster model

# we also need a database for the embeddings, use FAISS

# just mention we created a small function for adding new embeddings to the db

# process 100 or so articles to the db

# showcase how the very same article [side by side]
# which we couldn't find with imprecise/naive search methods, is found via semantics

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

# note ^
# Embed: "You are an embedding model." -> "summarize text" -> Last non-decoder LM layer is our Vec1
# Query: "What are you?" -> Embed query -> Vec2 -> Vec2 is similar to Vec1 -> retrieve: "You are an embedding model."

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

    # split each story into multiple, easy to describe chunks

    text_chunks = text_splitter.split_text(story.text)
    document_chunks = []

    for chunk in text_chunks:
        if is_text_junk(chunk):
            text_chunks.remove(chunk)
            continue

        # convert text to Document, to add metadata
        document_chunk = Document(page_content=chunk)
        document_chunk.metadata = story.document.metadata
        document_chunk.metadata["hn_title"] = story.title
        document_chunks.append(document_chunk)

    if len(document_chunks) != 0:
        vector_db.add_documents(documents=document_chunks, embeddings=embedder)
        print("story indexed:", story.title)


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
