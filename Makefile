build:
	poetry build

install:
	poetry install

test:
	poetry run pytest -s

run:
	poetry run uvicorn limnc_flaked.main:app --reload