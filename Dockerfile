FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY main.py /app/
# Expose the port that your application will listen on (Cloud Run/GCP)
EXPOSE 8080
#Set entrypoint
ENTRYPOINT ["python"]

CMD ["main.py"]
