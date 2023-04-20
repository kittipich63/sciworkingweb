# Start with a Python 3.9 image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install line-bot-sdk

RUN pip install -r requirements.txt

# Copy the project source code to the container
COPY . /app



