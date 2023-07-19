# Use the official lightweight Python image.
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy local code to the container image.
COPY . .

# Install production dependencies.
RUN pip install -r requirements.txt

# Set the command to start the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]