# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory into the container
COPY src /app

# Expose port 8000 for the FastAPI application
EXPOSE 8000

RUN python3 load_model.py

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
