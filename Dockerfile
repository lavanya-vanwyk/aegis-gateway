FROM python:3.10-slim

WORKDIR /app

# Prevent Python from writing pyc files to disc and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY requirements.txt .

# Get dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the prod server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]