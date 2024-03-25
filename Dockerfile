# FROM python:3.9.19-alpine3.18
FROM python:3.9-alpine3.15

WORKDIR /app

COPY ./Server /app/

RUN pip install --upgrade pip \
    && apk add --no-cache gcc musl-dev libsndfile-dev \
    && pip install librosa Flask flask_cors numpy
# RUN pip install --upgrade pip

# RUN pip install librosa
# RUN pip install Flask
# RUN pip install flask_cors
# RUN pip install numpy

EXPOSE 5000
CMD ["python", "main.py"]