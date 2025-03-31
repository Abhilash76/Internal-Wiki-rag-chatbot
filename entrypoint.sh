#!/bin/bash

##  Start Flask server in the background
#flask --app vector_api run --host=0.0.0.0 --port 5000 &

# Start Flask API server using Gunicorn in the background
gunicorn --bind 0.0.0.0:5000 vector_api:application &

# Start Streamlit app in the foreground
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0