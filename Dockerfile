# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libsasl2-dev \
    python-dev-is-python3 \
    libldap2-dev \
    libssl-dev \
    libpq-dev \
    gcc \
    build-essential && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app
# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies from the requirements.txt file (we'll create this next)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the Flask default port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]

