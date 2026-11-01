### validate:
--
`uv run ruff check .
uv run ruff format .
uv run python -c "from app.config.validator import validate_config; validate_config(); print('Configuration valid!')"
`
### run test
---
`uv run python -m pytest tests/test_config.py -v`

### lint: 
`uv run ruff check . --fix`                   
`uv run ruff format .`