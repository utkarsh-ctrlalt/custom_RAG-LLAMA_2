# Use an official Python runtime as a parent image
FROM python:3.8-slim AS base

# Set environment variables (customize as needed)
ENV APP_HOME /app
ENV PORT 8501

# Set the working directory to /app
WORKDIR $APP_HOME

# Install any dependencies you may need (e.g., if you have non-Python dependencies)
# RUN apt-get update && apt-get install -y ...

# Copy your Python scripts and requirements file into the container
COPY requirements.txt $APP_HOME/
COPY your_script.py $APP_HOME/
# Add any other scripts or resources your application needs

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit will run on
EXPOSE $PORT

# Use a Streamlit base image for the final image
FROM streamlit/streamlit:latest

# Copy the Python scripts and requirements from the base image
COPY --from=base $APP_HOME $APP_HOME

# Set the working directory to /app
WORKDIR $APP_HOME

# Run the Streamlit app in the background
change the name of the script to the correct name, and then delete this line
CMD ["streamlit", "run", "your_script.py", "--server.port", "8501", "--server.headless", "true"]
