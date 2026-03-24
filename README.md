# blog-utils

```
python -m blog_utils -f
python -m blog_utils -i html
python -m blog_utils -p html
python -m blog_utils -d
```

### Development Guide
#### With uv
```
uv sync --extra test
uv run ruff check
uv run pytest
```
#### Without uv
```
pip install -e '.[test]'
ruff check
pytest
```
