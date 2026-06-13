FROM --platform=$BUILDPLATFORM python:3.12

EXPOSE 8000

WORKDIR /app 

COPY requirements.txt /app

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app 

ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
