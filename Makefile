fastapi:
	uvicorn app.main:app --reload
	#uvicorn main:app --host localhost --port 8000 --workers 4
	#fastapi dev main.py

bot:
	python3 main.py



create_migrate:
	alembic init migrations

create_async_migrate:
	alembic init -t async migrations

makemigrations:
	alembic revision --autogenerate -m "Initial migration"

migrate:
	alembic upgrade head

down_migrate:
	alembic downgrade -1