# parent image
FROM python:3.8-slim

# set the working directory to /app
WORKDIR /app

# copy the current directory contents into the container at /app
COPY . .

# install dependencies from requirements.txt
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# copy the .env file to the container
COPY .env .

# run app.py with -u flag (shows the prints inside the container)
CMD ["python", "-u","app.py"] 

