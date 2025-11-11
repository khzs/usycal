# Use Ubuntu latest LTS as the base image
FROM ubuntu:latest

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install dependencies
RUN apt-get update && apt-get install -y \
    pipx \
    wget \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install project dependencies
COPY pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi
RUN poetry run playwright install --with-deps msedge

# Copy the rest of the application code
COPY main.py main.py
COPY calendar.ics calendar.ics

# Command to run the application
RUN ln -s /usr/bin/python3 /usr/bin/python
CMD ["poetry", "run", "python", "main.py"]
