#create a base image using python

FROM python:3.10-slim
# set the working directory in the container
WORKDIR /app
# copy the dependencies file to the working directory
COPY requirements.txt .
# install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# copy the content of the local src directory to the working directory
COPY /data /app/data
COPY /functions /app/functions
COPY dashboard.py /app/dashboard.py

EXPOSE 8080

# command to run on container start
CMD ["python", "dashboard.py"]