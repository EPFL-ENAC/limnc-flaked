build:
	poetry build

install:
	poetry install

test:
	poetry run pytest -s

run:
	poetry run uvicorn flaked.main:app --reload

workdir:
	rm -rf ./work
	mkdir -p ./work/instruments/instrument1/data
	touch ./work/instruments/instrument1/data/2021-01-01.csv
	touch ./work/instruments/instrument1/data/2021-01-02.csv
	touch ./work/instruments/instrument1/data/2021-01-03.csv
	mkdir -p ./work/instruments/instrument2/data
	touch ./work/instruments/instrument2/data/2025-01-01.csv
	touch ./work/instruments/instrument2/data/2025-01-02.csv
	touch ./work/instruments/instrument2/data/2025-01-03.csv
