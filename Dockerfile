# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: ENTERPRISE DEPLOYMENT CHASSIS (DOCKER WRAPPER)
# COMPLIANCE: ZERO EM-DASHES; ABSOLUTE PATH VIRTUALIZATION NATIVE
# ==============================================================================

FROM python:3.12-slim

# Establish the virtualized root workspace inside the container environment
ENV GOINGS_OS_ROOT=/opt/goings-os
WORKDIR $GOINGS_OS_ROOT

# Install systemic software dependencies required for high-volume SQLite and network routines
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy your local production script modules into the container image matrix
COPY . $GOINGS_OS_ROOT/

# Ingest official enterprise Google Cloud and Firebase framework libraries
RUN pip install --no-cache-dir \
    google-cloud-aiplatform \
    firebase-admin \
    asyncio

# Expose target networking communication ports for the live visual dashboard
EXPOSE 8080

# Launch the asynchronous background orchestration scheduler daemon on startup
CMD ["python", "orchestration_scheduler.py"]

# Use an official lightweight Node runtime as the parent image
FROM node:20-slim

# Set the working directory inside the container runtime sandbox
WORKDIR /usr/src/app

# Copy application dependency manifests to the container
COPY package*.json ./

# Install clean, production-only dependencies
RUN npm ci --only=production

# Copy the rest of your private kernel source code
COPY . .

# Expose port 8080 to match your Cloud Run settings
EXPOSE 8080

# Define the environment variable to run in production mode
ENV NODE_ENV=production

# The execution command to launch the Goings OS Engine
CMD [ "node", "server.js" ]
