import logging
import time

import streamlit as st
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Pinecone
from langchain_core.prompts import ChatPromptTemplate

import source
from vector_db import VectorDB

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


class App:
    # Create a prompt
    prompt = ChatPromptTemplate.from_template(
        """
    Answer the questions based on the provided context. Do not hallucinate.
    Please provide the most accurate response based on the question
    <context>
    {context}
    <context>
    Questions:{input}

    """
    )

    st.set_page_config(page_title="Chat with Wiki", page_icon=" ")

    st.title("RAG Chatbot")

    user_query = st.chat_input("Type your question here..")

    with st.chat_message("AI"):
        st.write("Hello, welcome to the chatbot application. I use Retrieval Augmented Generation "
                 "to give a comprehensive answer to your question based on the Documentation page of the PINExQ project")

    # Get the website url from the user
    with st.sidebar:
        st.header("Settings")
        website_url = st.text_input("Website Url")

    # Get Pinecone index
    index = VectorDB.index

    # Get index stats
    stats = index.describe_index_stats()

    @staticmethod
    def _format_time_duration(seconds: float) -> str:
        """
        Format time duration in a human-readable way using wall-clock time.
        Returns time in appropriate units (seconds or minutes)
        """
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        else:
            minutes = seconds / 60
            return f"{minutes:.2f} minutes"

    # Generate vector db from the website url
    @staticmethod
    def generate_vector_db(website_url=website_url, vdb=VectorDB()):
        if website_url:
            st.write("Generating vector embeddings for", website_url)
            vdb.vector_embedding(website_url)
        else:
            st.write("No url provided, generating vector embeddings for the PineXq documentation.")
            vdb.vector_embedding(source.get_source())

    # Check if there are any vectors in the index
    if stats.total_vector_count == 0:
        # No vectors in the index, generate new vectors
        LOG.info("No vectors found in the index. Generating new vectors...")
        generate_vector_db()
        LOG.info("Upsert into the VectorDB is complete.")
    else:
        # Vectors exist, perform similarity search
        LOG.info(f"Found {stats.total_vector_count} vectors in the index. Performing similarity search...")

    if user_query is not None and stats.total_vector_count > 0:
        # Create a response using the model and the embeddings
        # Using the time.time() for wall-clock time
        start_time = time.time()  # time.process_time()

        vdb = VectorDB()

        with st.status('Querying the Vector database..'):
            # Create a retriever
            vectorstore = Pinecone.from_existing_index(
                index_name="rag-index",
                embedding=vdb.embeddings,
                namespace="PINExQ")
            LOG.info(f"Printing to verify the embedding model used: {vdb.embeddings}")

            # Perform similarity search using the vectorstore
            results = vectorstore.similarity_search(user_query, k=10)
            LOG.info(f"Printing similarity search results here: {results}")

            retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

            # Create the document chain
            document_chain = create_stuff_documents_chain(VectorDB.model, prompt)
            retrieval_chain = create_retrieval_chain(retriever, document_chain)

        with st.status('Generating response..'):
            # Use the retrieved context to generate a response
            response = document_chain.invoke({'input': user_query, 'context': results})
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            formatted_time = _format_time_duration(elapsed_time)

            # Add response time to the message
            LOG.info(f"{response}\n\nResponse generated in {formatted_time}")

            # """with st.chat_message("AI"):
            #     st.write(response['answer'])"""

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Add new messages to history
        st.session_state.messages.append({"role": "Human", "content": user_query})
        st.session_state.messages.append({"role": "AI", "content": response})

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.sidebar:
            st.header("Settings")
            # With a streamlit expander
            with st.expander("Context"):
                # Find the relevant chunks
                st.write(results)
                st.write("--------------------------------")
