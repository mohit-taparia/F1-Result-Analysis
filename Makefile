.PHONY: help install test lint dbt-parse validate ingest-2024 load-2024 report report-watch report-clean

help:
	@echo "Modern F1 platform commands:"
	@echo "  make install      Install development, Snowflake, and dbt dependencies"
	@echo "  make test         Run non-live Python tests"
	@echo "  make lint         Run Python correctness linting"
	@echo "  make dbt-parse    Validate dbt structure without Snowflake"
	@echo "  make validate     Run lint, unit tests, and dbt structural validation"
	@echo "  make ingest-2024  Fetch/validate the 2024 season to local ignored RAW files"
	@echo "  make load-2024    Load 2024 into Snowflake RAW (requires credentials)"
	@echo ""
	@echo "Legacy academic report:"
	@echo "  make report"
	@echo "  make report-watch"
	@echo "  make report-clean"

install:
	python -m pip install -e ".[dev,snowflake,dbt]"

test:
	pytest -m "not live" -q

lint:
	ruff check src tests

dbt-parse:
	dbt parse --project-dir dbt --profiles-dir .github/dbt --no-partial-parse

validate: lint test dbt-parse

ingest-2024:
	f1-ingest --season 2024

load-2024:
	f1-load-snowflake --season 2024

report:
	latexmk -pdflatex -g -interaction=nonstopmode -outdir=build final_project.tex

report-watch:
	latexmk -pdflatex -pvc -e '$$pdf_previewer=q[open -a Skim]' -outdir=build final_project.tex

report-clean:
	latexmk -C *.tex
