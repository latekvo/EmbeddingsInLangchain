# compare search methods:
# - algolia API search (likely hybrid search)
# - trivial ctrl-f search (keyword search)
# - what can be actually seen in the story (purely vector search)
# try doing this in one file, that should make it much easier to read through for presentation's sake
import math

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api import get_stories
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

# fixme: ollama API deprecation warning

retrieved_stories = get_stories()

# init embedder

model = "nomic-embed-text:latest"

embedder = OllamaEmbeddings(model=model, base_url="http://localhost:11434")

# init vector db

vector_db = FAISS.from_texts(
    # this sample text will immediately be converted into an embedding
    ["You are an embedding model."],
    embedder,
)

# note ^
# Embed: "You are an embedding model." -> "summarize text" -> Last non-decoder LM layer is our Vec1
# Query: "What are you?" -> Embed query -> Vec2 -> Vec2 is similar to Vec1 -> retrieve: "You are an embedding model."

# init text splitter

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n\n", "\n\n", "\n", ". ", ", ", " ", ""],  # todo: explain or hide
    chunk_size=4096,  # usually smaller ones are recommended, todo: see what works best for HN
    chunk_overlap=math.ceil(4096 / 3),  # todo: explain
    keep_separator=False,
    strip_whitespace=True,
)

# embed all the stories
# todo: in python loops should be avoided, look for a better way

for story in retrieved_stories:
    if story.text is None:
        # story's URL likely 404'd
        print("story unavailable:", story.title)
        continue

    # split each story into multiple, easy to describe chunks

    chunks = text_splitter.split_text(story.text)

    for chunk in chunks:
        if is_text_junk(chunk):
            chunks.remove(chunk)
            continue

    if len(chunks) != 0:
        vector_db.add_texts(texts=chunks, embeddings=embedder)
        print("story indexed:", story.title)
