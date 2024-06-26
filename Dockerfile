# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory (our Flask app) into the container at /app
COPY . /app

# Install Flask and other dependencies
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt --root-user-action=ignore

# Make port 8080 available for the app
EXPOSE 8080

RUN chmod a+x docker-entrypoint.sh
CMD ["/app/docker-entrypoint.sh"]