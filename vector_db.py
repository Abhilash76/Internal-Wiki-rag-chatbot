import os
import logging

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from pinecone import Pinecone

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


class VectorDB:
    load_dotenv()
    base_url = os.getenv("OLLAMA_BASE_URL")

    # Initialize the model
    MODEL = "llama3.1"

    model = Ollama(model=MODEL, base_url=base_url)

    embeddings = OllamaEmbeddings(model=MODEL, base_url=base_url)

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("rag-index")
    index_name = "rag-index"

    @staticmethod
    def exists() -> bool:
        """
        Check if the vector database exists and contains vectors.

        Returns:
            bool: True if the index exists and contains vectors, False otherwise
        """
        try:
            # Check if the index exists in Pinecone
            active_indexes = VectorDB.pc.list_indexes()
            if VectorDB.index_name not in [index.name for index in active_indexes]:
                LOG.info(f"Index {VectorDB.index_name} does not exist in Pinecone")
                return False
            LOG.info(f"Found vectors in namespace")
            return True

        except Exception as e:
            LOG.error(f"Error checking vector database existence: {str(e)}")
            return False

    @staticmethod
    def vector_embedding(url):
        """ # Check if the index exists, if not create it
        if index not in pc.list_indexes(): # Failing to verify if the index already exists, Hence commenting.
            print(f"The index {index} does not exist in the list of pinecone indexes {pc.list_indexes()}")
            pc.create_index(
                name="rag-index",
                dimension=3072,  # Adjust this based on Ollama model's output
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )"""

        loader = WebBaseLoader(url)
        # Document Loading
        document = loader.load()
        # Chunk Creation
        # st.write(st.session_state.document)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # splitting
        final_documents = text_splitter.split_documents(document)
        # st.write("The splitted document chunks are: ", document)
        # vector Ollama embeddings
        LOG.info(f"The final document: {final_documents}")
        # Upserting generated embeddings into the VectorDB
        namespace = "PINExQ"
        VectorDB.upsert_documents(final_documents, namespace)

    @staticmethod
    def upsert_documents(final_documents, namespace):
        """
        Upserts documents into the Pinecone index with the required 'text' field in metadata.

        Args:
            final_documents (list): List of document objects to upsert.
            namespace (str): The namespace in Pinecone to upsert to.
        """
        # Extract texts and metadata, ensuring 'text' is included in metadata
        texts = [doc.page_content for doc in final_documents]
        metadatas = []

        for doc in final_documents:
            metadata = doc.metadata or {}  # Ensure metadata is not None
            metadata['text'] = doc.page_content
            metadatas.append(metadata)

        # Create embeddings for the documents
        _embeddings = VectorDB.embeddings.embed_documents(texts)

        # Create vectors for upsert
        vectors = [
            (f"doc_{i}", embedding, metadata)
            for i, (embedding, metadata) in enumerate(zip(_embeddings, metadatas))
        ]

        # Upsert to Pinecone
        VectorDB.index.upsert(vectors=vectors, namespace=namespace)

        LOG.info(f"Upserted {len(vectors)} vectors to namespace '{namespace}'")
