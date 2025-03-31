# Update Service

UpdateService is a REST service which allows to manage users and packages updates. It provides a set of APIs for:
- Update channels management
- Applications management
- Packages management
- User management

## Development

### Technology Stack

#### Runtime environment
- Docker (https://docs.docker.com/get-started/overview/)
- docker-compose for containers management and orchestration (https://docs.docker.com/compose/)
- Python 3.10

#### Third-party dependency management and build tool
- Poetry - dependency management and packaging tool (https://python-poetry.org/)
- Poe - task runner for poetry (https://github.com/nat-n/poethepoet)

#### Web/API framework
- REST API (https://docs.microsoft.com/uk-ua/azure/architecture/best-practices/api-design)
- FastAPI as API framework (https://fastapi.tiangolo.com/)
- Result: Swagger for created (auto-generated) API is available and exposed

##### Additional information
- [HTTP Protocol Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)

#### RDBMS
- Postgres 14
- SQLAlchemy ORM (https://www.sqlalchemy.org/)
- Alembic for schema and data migrations (https://alembic.sqlalchemy.org/en/latest/)


### Local dev env

Pre-requisites:
- Python 3.10
- Docker
- docker-compose
- poetry
- Poe

#### Build the app locally
```shell
poetry install
```

#### Run the app locally
```shell
poetry run uvicorn updateservice.app:app --host 0.0.0.0 --port 8080
```
Then open http://127.0.0.1:8080/docs in your browser


#### Run functional tests locally
poe local_api_test

#### Create DB migration


#### Upgrade DB schema
- poe alembic upgrade_heads_test
- poe alembic upgrade_heads_dev

#### Downgrade DB schema
- poe alembic downgrade_base_test
- poe alembic downgrade_base_dev

- Name : SANDU Robert-Andrei
- Personal email : san_roby@yahoo.com
