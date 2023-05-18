# Use Python ase base image
FROM python:3.11.3-slim

# Create an API directory in the container
WORKDIR /api

# copy the file to the container... I think this will go in the /api director?
COPY requirements.txt .

# install the requirements
RUN pip install -r requirements.txt

# Copy app.py - The . means copy to the working directory which is currently set to /api
COPY app.py .

# Copy the dbSecrets file which has the login info
COPY dbSecrets.py .

# Run app.py when the container launches
CMD ["python", "app.py"]
