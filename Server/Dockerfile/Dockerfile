FROM python:latest

WORKDIR /app

COPY ../ /app/

RUN pip3 install --upgrade pip

RUN pip3 install numpy Flask librosa flask_cors

EXPOSE 5000
CMD ["python", "main.py"]
# CMD ["sleep", "infinity"]