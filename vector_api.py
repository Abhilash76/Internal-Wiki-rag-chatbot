import logging

from flask import Flask, jsonify
from streamlit_app import App
from vector_db import VectorDB

"""This is a Flask app that instructs to generate the embeddings for the entire documentation"""

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class VectorDataInitializer:
    def __init__(self, rag):
        self.rag = rag  # Inject instance of APP
        self.vector_db = None
        # Register routes
        self.register_routes()

    def register_routes(self):
        @app.route('/generate', methods=['GET'])
        def generate_vectors():
            try:
                result = self.initialize()
                return jsonify({"status": "success", "message": result})
            except Exception as e:
                LOG.error(f"Error generating vectors: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 500

        @app.route('/status', methods=['GET'])
        def check_status():
            try:
                exists = self.vector_db.exists()
                return jsonify({
                    "status": "success",
                    "database_exists": exists
                })
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

    def initialize(self):
        """Initialize the vector database if it doesn't exist"""
        try:
            LOG.info("Initializing vector database")
            self.vector_db = VectorDB()
            # Check if Vector DB exists and create if it doesn't
            if not self.vector_db.exists():
                LOG.info("Creating vector database")
                result = self.rag.generate_vector_db()
                return jsonify(result=result)
            else:
                LOG.info("Vector database already exists")
            return True
        except Exception as e:
            LOG.error(f"Failed to initialize database: {str(e)}")
            raise


def create_app():
    """Application factory function"""
    try:
        rag = App()
        initializer = VectorDataInitializer(rag=rag)
        # Initial database check on startup
        initializer.initialize()
        return app
    except Exception as e:
        LOG.error(f"Failed to create app: {str(e)}")
        raise


# Create the application instance
application = create_app()

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000, debug=True)  # debug=True for debugging
