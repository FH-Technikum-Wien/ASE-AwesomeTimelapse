# Use the official Python image from the Docker Hub
FROM python:3.8.2

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Make a new directory to put our code in.
RUN mkdir /code

# Change the working directory. 
# Every command after this will be run from the /code directory.
WORKDIR /code

# Copy the requirements.txt file.
COPY ./requirements.txt /code/

# Install the requirements.
RUN pip install -r requirements.txt

# Copy the rest of the code.
COPY . /code/

#ENTRYPOINT ["python", "/code/vb_worker.py"]