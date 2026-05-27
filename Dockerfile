FROM python:3.12-slim

ARG REQUIREMENTS=requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

COPY requirements/ /requirements/

RUN pip install -r /requirements/${REQUIREMENTS}

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["sh", "./entrypoint.sh"]
