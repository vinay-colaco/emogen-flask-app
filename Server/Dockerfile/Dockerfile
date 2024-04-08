FROM python:3.9.18

WORKDIR /app

COPY ./requirement.txt /app/

RUN pip3 install --upgrade pip

RUN pip install --no-cache-dir -r requirement.txt

COPY ../ /app/

EXPOSE 5000

CMD ["python", "main.py"]
# CMD ["sleep", "infinity"]