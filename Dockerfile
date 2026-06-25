FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and build frontend
COPY forgeai-studio/frontend ./frontend
RUN cd frontend && npm install && npm run build

# Copy backend
COPY forgeai-studio/backend ./backend

# Install Python dependencies
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

EXPOSE 8000

# Run from backend dir so relative imports work
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
