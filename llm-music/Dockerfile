# Use a Python base image with a recent version
FROM python:3.9-slim-buster

# Install necessary system packages for Ollama and building Python packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Ollama
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models 
# Standard Ollama model storage path

# Install Ollama
# This command downloads and executes the official Ollama installer script
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
# This helps speed up rebuilds if only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
# The '.' refers to the current directory (llm-music in your case)
COPY . .

# Pull the Gemma 3n model during the image build process
# This ensures the model is available when the container starts
RUN ollama pull gemma3n

# Expose the port your Python web server will listen on
# IMPORTANT: Ensure your web_server.py listens on this port (e.g., 8080)
EXPOSE 8080

# Create an entrypoint script
# This script will ensure Ollama server is running before your Python app starts
COPY start.sh .
RUN chmod +x start.sh

# Use the entrypoint script as the command to run when the container starts
ENTRYPOINT ["./start.sh"]