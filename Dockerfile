FROM python:3.10-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add gcc libc-dev libffi-dev
RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app_migrations

COPY alembic.ini poetry.lock pyproject.toml .env.test /app_migrations/
RUN mkdir /app_migrations/migrations
COPY /migrations/ /app_migrations/migrations/
# hack to avoid rebuilding the wheel every time the source code changes
RUN mkdir /app_migrations/updateservice && touch /app_migrations/updateservice/app.py && poetry build -f wheel
COPY ./updateservice /app_migrations/updateservice
FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY --from=builder /app_migrations /app/
RUN python3 -m pip install poetry
RUN poetry install
COPY --from=builder /app_migrations/dist/updateservice*.whl /app/
RUN pip3 install updateservice*.whl

EXPOSE 8080
CMD ["uvicorn", "updateservice.app:app", "--host", "0.0.0.0", "--port", "8080"]
