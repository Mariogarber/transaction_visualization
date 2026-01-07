# Create a base image using Python
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the working directory
COPY . /app/

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8080

# Command to run the application with gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 300 --access-logfile - --error-logfile - app:server"]