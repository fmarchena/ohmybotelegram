FROM python:3.9

WORKDIR /app

COPY script.py /app/extract_env.py
RUN pip install docker

CMD ["python", "/app/extract_env.py"]