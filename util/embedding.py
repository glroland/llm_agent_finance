from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()


def init_embedding_model():
    embedding = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
    return embedding


# recursively split and chunk langchain documents
def rec_split_chunk(documents, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    chunked_docs = text_splitter.split_documents(documents)
    return chunked_docs
