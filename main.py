# compare search methods:
# - algolia API search (likely hybrid search)
# - trivial ctrl-f search (keyword search)
# - what can be actually seen in the story (purely vector search)
# try doing this in one file, that should make it much easier to read through for presentation's sake

from api import get_stories

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

retrieved_stories = get_stories()
print(retrieved_stories)
