FROM python:3.12-slim
WORKDIR /app
COPY server.py db.py /app/
EXPOSE 55555
CMD ["python", "server.py"]