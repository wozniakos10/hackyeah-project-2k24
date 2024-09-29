FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \ 
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Set PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Copy only requirements to cache them in Docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy project files
COPY . /app

EXPOSE 8501

ENTRYPOINT ["poetry", "run", "streamlit", "run", "src/hackyeah_project_lib/web/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
