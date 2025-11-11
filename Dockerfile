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

# Install Microsoft Edge
RUN wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" \
    && apt-get update \
    && apt-get install -y microsoft-edge-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install project dependencies
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Command to run the application
RUN ln -s /usr/bin/python3 /usr/bin/python
CMD ["poetry", "run", "python", "main.py"]
