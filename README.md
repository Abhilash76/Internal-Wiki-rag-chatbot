# Introduction 
This is a repository of a chatbot that provides quick and accurate answers from the organizational wiki, enhancing the efficiency of retrieving important information. The chatbot uses Natural Language Processing (NLP) techniques and Retrieval Augmented Generation (RAG) to deliver concise and contextually relevant responses to user queries.

#Features
###NLP-powered Chatbot: 
Retrieves information from organization's wiki with high accuracy.
###RAG Architecture: 
Combines retrieved data with generative capabilities for more context-aware answers.
###LLaMA 3.1 Model: 
Leverages the power of the LLaMA (Large Language Model Meta AI) 3.1 model for generating high-quality answers.
###Streamlit Interface: 
Provides a simple and interactive UI to communicate with the chatbot.

# Getting Started
##Prerequisites
###Docker: 
Ensure that Docker is installed and running on your machine. We will use Docker to run both the chatbot and the Ollama container required to pull the LLaMA 3.1 model.
###Ollama: 
This repository provides access to various open-source Large Language Models (LLMs), including LLaMA. It will be used to pull and run the LLaMA 3.1 model.

##Installation process
###Install Dependencies:
You’ll need a few more dependencies to set up the chatbot. Install the required libraries from the requirements.txt:

    pip install -r requirements.txt

#Running with Docker
We run the chatbot using Streamlit on localhost:8501, with the LLaMA 3.1 model running in the background using the Ollama Docker image. This setup ensures the model can be used for generating responses in real time.
Since all the parameters have been configured in the docker-compose file, Run the docker-compose file in order to get the application running.

    docker compose up -d

The chatbot will be running on the port 8501. Navigate to localhost:8501 to use the chatbot.

#Possible bugs
1. If the responses are not getting generated as predicted or the context to generate the answers is null, update the Vector DB with the documentation with a GET request using the Flask app.
2. Make sure to update the vectors in the same namespace in the pinecone-index in which the similarity score is performed to avoid any out-of-context answers.
3. Check and update the version of Ollama if the error string contains "Max retries exceeded".

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 