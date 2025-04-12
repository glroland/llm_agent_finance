from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
import os
import argparse
import embedding


class ChromaDatabase:
    def __init__(
        self,
        collection_name=None,
        persist_directory=None,
        chunk_size=None,
        chunk_overlap=None,
    ):
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME")
        self.persist_directory = os.getenv("CHROMA_PERSIST_PATH")
        self.chunk_size = int(os.getenv("CHUNK_SIZE"))
        self.chunk_overlap = int(os.getenv("OVERLAP"))
        self.embedding_model = embedding.init_embedding_model()

    def load_documents(self, directory):
        """Loads documents from a directory using LangChain's DirectoryLoader."""
        print("Loading documents as LangChain documents")
        loader = DirectoryLoader(directory, use_multithreading=True, show_progress=True)
        docs = loader.load()
        print(f"Loaded {len(docs)} docs")
        return docs

    def chunk_documents(self, docs):
        """Splits and chunks documents for embedding."""
        print(
            f"Splitting and chunking documents (chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap})"
        )
        return embedding.rec_split_chunk(
            docs, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

    def upload_to_collection(self, chunked_documents):
        """Uploads chunked documents to a Chroma collection."""
        print(
            f"Uploading {len(chunked_documents)} documents to Chroma collection: {self.collection_name}"
        )
        vectordb = Chroma.from_documents(
            collection_name=self.collection_name,
            documents=chunked_documents,
            embedding=self.embedding_model,
            persist_directory=self.persist_directory,
        )

        return vectordb

    def batch_process(self, chunked_documents, batch_size=41000):
        """Processes documents in batches to optimize memory usage."""
        total_batches = (len(chunked_documents) + batch_size - 1) // batch_size
        for i in range(0, len(chunked_documents), batch_size):
            batch = chunked_documents[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            print(
                f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)"
            )
            vectordb = self.upload_to_collection(batch)
            print(f"Batch {batch_num} complete and persisted")

    def query(self, query_text, n_results=5):
        """Queries the vector database."""
        db = self.get_vector_db()
        return db.query(query_texts=query_text, n_results=n_results)

    def get_vector_db(self):
        """Initializes and returns the Chroma vector database instance."""
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="upload docs to chromadb",
        description="Load files in directory to Chroma vector db",
    )

    parser.add_argument("directory", type=str, help="Location of file directory")
    args = parser.parse_args()

    # Instantiate and run the pipeline
    chroma_db = ChromaDatabase()
    documents = chroma_db.load_documents(args.directory)
    chunked_docs = chroma_db.chunk_documents(documents)
    chroma_db.batch_process(chunked_docs)

    # Verify the documents were uploaded
    db = chroma_db.get_vector_db()
    collection = db.get()
    print(
        f"\nVerification: Collection '{chroma_db.collection_name}' now contains {len(collection['ids'])} documents"
    )
    print("Chroma database upload complete!")
