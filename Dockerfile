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
