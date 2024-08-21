# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /AI-Assistant

# Copy the Pipfile and Pipfile.lock first, to leverage Docker cache
COPY Pipfile Pipfile.lock ./

# Install pipenv
RUN pip install pipenv

# Install dependencies using Python 3.10 explicitly
RUN pipenv install --deploy --ignore-pipfile --python /usr/bin/python3.10

# Copy the rest of the application code
COPY . .

# Expose the Streamlit port (default is 8501)
EXPOSE 8501

# Set the command to run Streamlit
CMD ["pipenv", "run", "streamlit", "run", "UI.py"]
