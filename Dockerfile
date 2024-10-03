# app/Dockerfile
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Run database migrations and then start the application
ENTRYPOINT ["sh", "-c"]

# Use CMD to run migrations and then start the server
CMD ["python manage.py migrate && gunicorn --bind 0.0.0.0:8000 nail-be.wsgi:application"]
