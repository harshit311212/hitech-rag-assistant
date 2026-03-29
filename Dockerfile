# Use official Python runtime as a secure base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Ensure tzdata and essential build tools are present for FAISS
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace embedding model at build time to prevent runtime Connection Errors
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy the rest of the application code
COPY . .

# Expose port (Railway dynamically injects $PORT)
EXPOSE 8501

# Run the Streamlit app securely, binding to 0.0.0.0 and ignoring CORS for deployment
CMD streamlit run app.py \
    --server.port ${PORT:-8501} \
    --server.address 0.0.0.0
