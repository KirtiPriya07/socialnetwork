FROM python:3

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create a directory for the app
RUN mkdir /socialnetwork
WORKDIR /socialnetwork

# Copy requirements file and install dependencies
COPY requirements.txt /socialnetwork/
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /socialnetwork/

# Expose the port your app runs on (e.g., 8000)
EXPOSE 8001

# Command to run the application (change 'manage.py' to your main entry point)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001","0.0.0.0"]
