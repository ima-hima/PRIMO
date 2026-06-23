# Stage 1: Build React bundle
FROM node:20-slim AS react-builder
WORKDIR /build
COPY src/tree-view-app/package*.json ./
RUN npm install --legacy-peer-deps
COPY src/tree-view-app/src ./src
COPY src/tree-view-app/public ./public
ENV GENERATE_SOURCEMAP=false
ENV PUBLIC_URL=/static/primo/react
RUN npm run build

# Stage 2: Python app
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

RUN mkdir -p /react-static
COPY --from=react-builder /build/build/ /react-static/

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["sh", "./entrypoint.sh"]
